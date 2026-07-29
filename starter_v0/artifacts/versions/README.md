# Artifact version snapshots

Each folder records the exact prompt and tool declaration used by a valid base-eval run.

- `v0` and `v1` share the baseline artifacts; v1 records the first measured iteration.
- `v2` and `v3` share the final optimized artifacts.
- `metadata.json` stores the full SHA-256 hashes and the matching run log.
- The runnable artifacts remain at `artifacts/system_prompt.md` and `artifacts/tools.yaml`; they mirror `versions/v3/` so existing commands continue to work.

