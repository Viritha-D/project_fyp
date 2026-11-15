# Learned store

`learned.jsonl` holds the module's suggestions, one JSON record per line. It is plain git, not Git LFS, and lives outside
every frozen path.

- **Created as needed.** The file is created on the first suggestion made in live mode.
- **Unverified by default.** Every record starts as `unverified`. Use `python -m selflearn.verify` to list records and
  mark them `verified` or `rejected`, giving who checked and how.
- **Never evidence.** Unverified records never count as evidence for confidence.
- **Read-only when hosted.** In the hosted (cloud) app the store is read-only, because that file system is not durable.
