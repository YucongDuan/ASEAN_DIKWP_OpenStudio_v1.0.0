# Security and data handling

The offline edition runs locally and makes no model or analytics requests. It never executes selected repositories. Local exports may contain a student's own text; students choose when to share them. Browser storage can be cleared by the browser or machine owner and should not be treated as a secure archive.

The WSGI edition stores salted scrypt password hashes, hashed session tokens, private project revisions and explicit class submissions. Mutating endpoints require same-origin JSON and authenticated CSRF tokens. Teacher roles are provisioned at the local command line. Static serving is restricted to the web directory and allowed file types. Code archives are inspected with path, size, compression and file-type checks before extraction.

This release has behavioral and input-validation tests, not an independent penetration test or security certification. Run the provided local server only on loopback. For shared institutional use, provide HTTPS, reverse-proxy access/rate controls, maintained dependencies, private backups and the institution's own user-account lifecycle. Password recovery and institutional SSO are not implemented.

When reporting a defect, share a minimal synthetic reproduction and affected version; omit student records, session cookies, passwords and private project content. No public reporting email or repository URL is invented before the maintainer chooses a publication destination.
