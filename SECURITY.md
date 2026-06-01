# Security Policy

## Reporting a vulnerability

Email **brad@bradmlindsey.com** with a description and reproduction steps.
Please do not open a public issue for security-sensitive reports.

## Authorship signatures

This project's authorship ledger is signed with an Ed25519 key.

- The **public** key is committed at [`keys/brad_authorship.pub`](keys/brad_authorship.pub).
- The **private** key is **never committed** (`*.key` is git-ignored).
- The signature-verification procedure is documented in the README under **Verification**.

If a signature fails to verify against the committed public key, treat the
artifact as unverified and contact the address above.
