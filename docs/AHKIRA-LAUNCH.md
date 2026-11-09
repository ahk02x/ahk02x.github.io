# ahkira launch gate

The /ask/ page is integrated in the portfolio branch. This is frontend preparation, not proof of a working public API.

Before merging this branch for public launch:

- Reconcile the Worker knowledge pack with the approved public site copy; the deployed pack still contains the older About text.
- Verify the exact deployed Worker code against the reviewed source and complete the device/service pre-run audit.
- Preserve existing security headers while allowing https://challenges.cloudflare.com in script-src and frame-src for Turnstile.
- Connect ahk02x.dev/api/ask* to the existing production ahkira-bot Worker. Keep workers.dev disabled. A static GitHub Pages deployment alone cannot answer this API path.
- Confirm /api/ask/health returns the expected ready state, a real browser question receives a model answer, and storage records the redacted turn.

The prepared questions work without the Worker. Local previews do not provide the production API or a valid production-host Turnstile token.

Rollback: set the documented manual nap keys, remove the API route, and revert the site launch commit if needed. Do not remove data or secrets as a rollback shortcut.

No Cloudflare configuration was changed during this integration.
