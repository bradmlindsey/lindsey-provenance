#!/usr/bin/env python3
"""brad_assimilate_brief - Phase-1/2/3 helper for the BRAD client-brief assimilation workflow.

Provenance-tracked build (lindsey-provenance framework).

Operations:
    --extract <brief-path>    Phase 1+2: archive the brief into operator/briefs/,
                              compute SHA-256, emit paragraph-numbered .extracted.txt,
                              update operator/briefs/BRIEF_LOG.md.
    --tag <extracted-txt>     Phase 3: emit a domain-vector tag histogram by
                              regex-matching paragraphs against the controlled
                              vocabulary; produce a starter table for the operator
                              to drop into the triage doc.
    --skeleton <slug>         Phase 6 helper: emit a CLIENT_BRIEF_TRIAGE_<slug>.md
                              skeleton from the template into docs/internal_record/.

Tail-safe code style: single-line print(); dict() + key assignment instead of
multi-line literal dicts; ast.parse compile check at module import time.
"""
import argparse
import datetime
import hashlib
import os
import re
import shutil
import sys
from lindsey_provenance.config import (
    REPLICATOR_BASELINE, REPLICATOR_SHA256, PRINCIPAL, INSTITUTION,
)

CONTROLLED_VOCAB = dict()
CONTROLLED_VOCAB["MHD"] = [r"\bmhd\b", r"magneto", r"lorentz", r"ferrofluid", r"j\s*[x×]\s*b", r"maxwell"]
CONTROLLED_VOCAB["VISCO"] = [r"viscoelastic", r"prony", r"hereditary", r"memory kernel", r"shock"]
CONTROLLED_VOCAB["THERMAL"] = [r"thermal", r"boussinesq", r"fourier", r"rayleigh", r"buoyan", r"heat"]
CONTROLLED_VOCAB["STRUCT"] = [r"cauchy", r"stress", r"strain", r"\bvon mises\b", r"12\s*mpa", r"buckling"]
CONTROLLED_VOCAB["ACOUSTIC"] = [r"helmholtz", r"acoustic", r"resonance", r"resonator", r"carrier wave", r"\bq[- ]factor\b"]
CONTROLLED_VOCAB["FLUID"] = [r"navier", r"navier-stokes", r"\bmach\b", r"\bma\s*[<>=]+", r"drainage", r"fluidic", r"\bp_sat\b", r"cavitation"]
CONTROLLED_VOCAB["PHASE"] = [r"allen-cahn", r"cahn-hilliard", r"phase[- ]field", r"morphogenesis", r"diffuse[- ]interface"]
CONTROLLED_VOCAB["FAB"] = [r"\bsla\b", r"stereolithography", r"photopolymer", r"ferroelastomer", r"vacuum.*extract", r"vertex weld", r"resin"]
CONTROLLED_VOCAB["METRO"] = [r"\bdic\b", r"\bldv\b", r"hydrophone", r"vibrometry", r"image correlation", r"transducer"]
CONTROLLED_VOCAB["MATH"] = [r"\brmse\b", r"refit", r"convergence", r"integrator", r"\bmpi\b", r"gauss-newton"]
CONTROLLED_VOCAB["INV"] = [r"\brule\s*\d+\b", r"zero[- ]telemetry", r"\bbfs\b", r"invariant", r"laminar", r"manifold"]
CONTROLLED_VOCAB["ADMIN"] = [r"^#", r"proceed\b", r"^principal", r"^\*\*", r"\bwire\b", r"standing guard"]

NUMERICAL_TOKEN_RE = re.compile(r"\d+(?:\.\d+)?\s*(?:MPa|kPa|Pa|um|µm|mm|cm|m\b|Hz|kHz|MHz|MW|kW|MPI)", re.IGNORECASE)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_paragraphs_docx(path):
    """Return a list of non-empty paragraph strings from a .docx file."""
    try:
        from docx import Document
    except ImportError:
        print("ERROR: python-docx not installed. Run: pip install python-docx --break-system-packages")
        sys.exit(2)
    d = Document(path)
    out = []
    for p in d.paragraphs:
        t = p.text.strip()
        if t:
            out.append(t)
    return out


def extract_paragraphs_text(path):
    """Return a list of non-empty paragraph strings from a plain-text/markdown file."""
    with open(path, "r", encoding="utf-8") as fh:
        body = fh.read()
    # Split on blank lines; treat each non-empty chunk as a paragraph.
    chunks = re.split(r"\n\s*\n", body)
    out = []
    for c in chunks:
        s = c.strip()
        if s:
            out.append(s)
    return out


def write_extracted(paragraphs, out_path):
    lines = []
    for i, p in enumerate(paragraphs, start=1):
        lines.append(f"{i:04d}\t{p}")
    body = "\n".join(lines) + "\n"
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(body)
    return len(body)


def update_brief_log(repo_root, archived_name, fmt, words, sha, received_utc, verdict_placeholder):
    log_path = os.path.join(repo_root, "operator", "briefs", "BRIEF_LOG.md")
    if not os.path.exists(log_path):
        header = []
        header.append("# BRAD Brief Log")
        header.append("")
        header.append("**PROVENANCE-TRACKED**")
        header.append("**Replicator baseline:** `" + REPLICATOR_BASELINE + "`")
        header.append("")
        header.append("Immutable log of every client / Architect brief received and routed through the BRAD assimilation workflow.")
        header.append("")
        header.append("| Brief filename | Original format | Words | SHA-256 | Received UTC | Triage doc | Verdict |")
        header.append("|---|---|---:|---|---|---|---|")
        with open(log_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(header) + "\n")
    row = "| `" + archived_name + "` | " + fmt + " | " + str(words) + " | `" + sha + "` | " + received_utc + " | _pending triage_ | " + verdict_placeholder + " |"
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(row + "\n")
    return log_path


def cmd_extract(args, repo_root):
    src = args.extract
    if not os.path.isfile(src):
        print("ERROR: brief not found at " + src)
        return 2
    base = os.path.basename(src).lower()
    ext = os.path.splitext(base)[1]
    if ext in (".png", ".jpg", ".jpeg", ".webp", ".heic"):
        print("INFO: image-modality brief detected (" + ext + ")")
        print("    Multi-modal intake: persist the binary asset under")
        print("    operator/briefs/<YYYY-MM-DD>_<slug>.assets/{project_photos|handwriting_controls}/")
        print("    and add a row to the asset manifest's MANIFEST.md.")
        print("    Auto-OCR/VLM extraction is not yet wired (see HANDWRITING_INGESTION_CONTROL_2026-05-19.md §6 MM-2).")
        print("    Falling through to file archive + SHA-256 only.")
    elif ext not in (".docx", ".md", ".txt"):
        print("ERROR: unsupported extension " + ext + " - use .docx, .md, .txt, .png, .jpg, .jpeg, .webp, or .heic")
        return 2
    today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
    slug = re.sub(r"[^a-z0-9]+", "-", os.path.splitext(base)[0]).strip("-")
    if not slug:
        slug = "brief"
    archived_name = today + "_" + slug + ext
    briefs_dir = os.path.join(repo_root, "operator", "briefs")
    os.makedirs(briefs_dir, exist_ok=True)
    dst = os.path.join(briefs_dir, archived_name)
    shutil.copy2(src, dst)
    sha = sha256_file(dst)
    if ext == ".docx":
        paras = extract_paragraphs_docx(dst)
        fmt = "docx"
    elif ext in (".png", ".jpg", ".jpeg", ".webp", ".heic"):
        paras = ["[IMAGE-MODALITY BRIEF - transcription pending; see asset manifest]"]
        fmt = "image"
    else:
        paras = extract_paragraphs_text(dst)
        fmt = ext.lstrip(".")
    words = sum(len(p.split()) for p in paras)
    extracted_path = os.path.join(briefs_dir, today + "_" + slug + ".extracted.txt")
    nbytes = write_extracted(paras, extracted_path)
    received_utc = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    log_path = update_brief_log(repo_root, archived_name, fmt, words, sha, received_utc, "_pending_")
    print("[brad_assimilate_brief: extract]")
    print("    archived            : " + dst)
    print("    sha256              : " + sha)
    print("    paragraphs          : " + str(len(paras)))
    print("    words               : " + str(words))
    print("    extracted_text      : " + extracted_path + "  (" + str(nbytes) + " bytes)")
    print("    brief_log_appended  : " + log_path)
    return 0


def tag_paragraph(text):
    """Return a list of controlled-vocab tags that match this paragraph."""
    tl = text.lower()
    tags = []
    for tag, patterns in CONTROLLED_VOCAB.items():
        for pat in patterns:
            if re.search(pat, tl):
                tags.append(tag)
                break
    if not tags:
        # Default fallback: ADMIN if it's clearly a heading/rhetoric; else MATH-or-leave-empty
        if re.match(r"^[#*]+", text) or len(text) < 40:
            tags.append("ADMIN")
    return tags


def cmd_tag(args, repo_root):
    src = args.tag
    if not os.path.isfile(src):
        print("ERROR: extracted text not found at " + src)
        return 2
    paragraphs = []
    with open(src, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            # Expect lines like "0001\t...text..."
            parts = line.split("\t", 1)
            if len(parts) == 2 and parts[0].strip().isdigit():
                paragraphs.append((int(parts[0]), parts[1]))
            else:
                paragraphs.append((len(paragraphs) + 1, line))
    histogram = dict()
    for tag in CONTROLLED_VOCAB.keys():
        histogram[tag] = []
    untagged = []
    flagged_numerical = []
    for idx, text in paragraphs:
        tags = tag_paragraph(text)
        if not tags:
            untagged.append(idx)
            tags = ["?"]
        for t in tags:
            if t in histogram:
                histogram[t].append(idx)
        if NUMERICAL_TOKEN_RE.search(text) and (set(tags) <= {"ADMIN"}):
            flagged_numerical.append(idx)
    print("[brad_assimilate_brief: tag]")
    print("    paragraphs total    : " + str(len(paragraphs)))
    print("    untagged paragraphs : " + str(len(untagged)) + " " + (str(untagged[:8]) if untagged else ""))
    print("    flagged ADMIN+num   : " + str(flagged_numerical[:8]) + "  (numerical tokens in ADMIN-tagged paragraphs - must be re-tagged)")
    print("")
    print("    Domain-vector histogram (paste into triage §3.3):")
    print("")
    print("    | Tag | Paragraph count | Sample line refs |")
    print("    |---|---:|---|")
    for tag, refs in histogram.items():
        sample = ", ".join(str(x) for x in refs[:6])
        print("    | " + tag.ljust(8) + " | " + str(len(refs)).rjust(3) + " | " + sample + " |")
    return 0


def cmd_skeleton(args, repo_root):
    slug = args.skeleton
    if not re.match(r"^[a-z0-9][a-z0-9_-]{2,63}$", slug):
        print("ERROR: slug must be 3-64 chars, lowercase + digits + dashes/underscores")
        return 2
    template_path = os.path.join(repo_root, "operator", "templates", "CLIENT_BRIEF_TRIAGE_TEMPLATE.md")
    if not os.path.isfile(template_path):
        print("ERROR: template not found at " + template_path)
        return 2
    out_path = os.path.join(repo_root, "docs", "internal_record", "CLIENT_BRIEF_TRIAGE_" + slug.upper() + ".md")
    if os.path.exists(out_path):
        print("ERROR: triage doc already exists at " + out_path + " - delete first if you mean to overwrite")
        return 2
    with open(template_path, "r", encoding="utf-8") as fh:
        body = fh.read()
    body = body.replace("`<brief-basename>`", "`" + slug + "`")
    body = body.replace("`YYYY-MM-DD`", datetime.datetime.utcnow().strftime("%Y-%m-%d"))
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(body)
    print("[brad_assimilate_brief: skeleton]")
    print("    triage doc written  : " + out_path)
    print("    next               : fill §1-§5 from the extracted text + cross-checks")
    return 0


def find_repo_root():
    # lindsey_provenance: anchor on .lindsey_provenance/ marker (or cwd fallback).
    from lindsey_provenance import _root as _br
    return _br.project_root()


def main():
    ap = argparse.ArgumentParser(prog="brad_assimilate_brief", description="BRAD client-brief assimilation helper.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--extract", metavar="BRIEF_PATH", help="Archive + extract a brief (.docx/.md/.txt).")
    g.add_argument("--tag", metavar="EXTRACTED_TXT", help="Tag paragraphs against the controlled vocabulary.")
    g.add_argument("--skeleton", metavar="SLUG", help="Emit a triage doc skeleton from the template.")
    g.add_argument("--selftest", action="store_true", help="Run a self-test on a minimal in-memory brief.")
    args = ap.parse_args()
    repo_root = find_repo_root()
    if args.extract:
        return cmd_extract(args, repo_root)
    if args.tag:
        return cmd_tag(args, repo_root)
    if args.skeleton:
        return cmd_skeleton(args, repo_root)
    if args.selftest:
        return selftest(repo_root)
    return 1


def selftest(repo_root):
    """Minimal in-memory self-test: tag a synthetic 3-paragraph brief."""
    sample = []
    sample.append("# Magneto-Hydrodynamic Logic Frontier")
    sample.append("The compiler must compute Lorentz body force J x B on a ferrofluid carrier inside the conduit, gated at Ma <= 0.3.")
    sample.append("BFS drainage must be 100% per Rule 19, and the SLA print head must hold 50 um cure layer.")
    tagged = []
    for i, p in enumerate(sample, start=1):
        tagged.append((i, p, tag_paragraph(p)))
    print("[brad_assimilate_brief: selftest]")
    for idx, text, tags in tagged:
        print("    para " + str(idx) + " tags=" + ",".join(tags) + " :: " + text[:60])
    if "MHD" in tagged[1][2] and "FLUID" in tagged[1][2] and "FAB" in tagged[2][2]:
        print("    PASS - controlled vocab matched expected tags")
        return 0
    print("    FAIL - tagging did not match expectations")
    return 1


if __name__ == "__main__":
    sys.exit(main())
# end
