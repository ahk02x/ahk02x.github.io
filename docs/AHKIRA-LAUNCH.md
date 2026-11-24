# ahkira launch gate — closed

The /ask/ page is live on ahk02x.dev and `/api/ask/health` answers `{"state":"ok"}` on the production host.
Checked 2026-11-16 from this branch. The site copy on this branch says ahkira is public, which is why the
"coming soon" tab is gone: `src/pages/ahkira-next.html` and its tab strip in `build.py` were removed, and the
one real roadmap item on it (rate limits that cannot be overrun) moved to the ask page's Planned list.

What the gate asked for, and where it stands:

- Worker knowledge pack reconciled with the public copy — the deployed pack answers from the public pages. Any
  copy change on this branch that the pack quotes needs the pack rebuilt before it is true.
- The Worker is connected to ahk02x.dev/api/ask*, workers.dev stays disabled, Turnstile is allowed in
  script-src and frame-src, and the health route answers ready.
- Still open, and not a launch blocker: the nightly attack re-runs, and rate limits that cannot be overrun.

Local previews still do not provide the production API or a valid production-host Turnstile token: a typed
question in a plain file-server preview always fails the bot check. The prepared questions work without it.

Rollback is unchanged: set the documented manual nap keys, remove the API route, revert the launch commit.
Never remove data or secrets as a rollback shortcut.
