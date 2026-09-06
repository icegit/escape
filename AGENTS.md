# Repository preferences

- After completing each requested change, run the relevant checks, commit the
  task's changes, push to `origin/main`, and verify GitHub Pages deployment.
  The user explicitly wants automatic push and deployment for this repository;
  do not stop at local edits or ask for routine deployment confirmation.
- When a change affects the Garmin integration or health overview, also run
  `sync-garmin-weight.yml` and verify the updated data on the live site.
- Preserve unrelated local changes and private Garmin exports. Never commit
  credentials, authentication tokens or the full private export.
- Deployment target: https://icegit.github.io/escape/ (GitHub Pages, main branch).
