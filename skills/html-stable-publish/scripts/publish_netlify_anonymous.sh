#!/usr/bin/env bash
# Publish a preflighted static directory as a temporary anonymous Netlify deploy.
# The platform requires a project to be claimed within one hour for later management.
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  publish_netlify_anonymous.sh --source <directory> [--dry-run]

Runs `netlify deploy --dir <directory> --allow-anonymous` only after the user has
explicitly approved public anonymous upload. The resulting link is temporary: claim
it within one hour only if the user later chooses to create/login to a Netlify account.
EOF
}

SOURCE=""
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --source) SOURCE="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "ERROR: Unknown argument: $1" >&2; usage >&2; exit 64 ;;
  esac
done

[[ -n "$SOURCE" ]] || { echo "ERROR: --source is required" >&2; usage >&2; exit 64; }
SOURCE="$(cd "$SOURCE" && pwd)"
[[ -f "$SOURCE/index.html" ]] || { echo "ERROR: source root must contain index.html" >&2; exit 65; }

printf 'TARGET_PLATFORM=Netlify anonymous deploy\nSOURCE=%s\nEXPECTED_LINK_LIFECYCLE=temporary; claim window is 1 hour\n' "$SOURCE"
if [[ "$DRY_RUN" -eq 1 ]]; then
  cat <<'EOF'
DRY_RUN=true
No external changes were made. A real run will first preflight the site, then publicly upload it with:
  netlify deploy --dir <source> --allow-anonymous
Do not describe the resulting URL as permanent or manageable without an account.
EOF
  exit 0
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/preflight_static_site.py" "$SOURCE"
command -v netlify >/dev/null || {
  echo "ERROR: Netlify CLI is not installed. Install it with: npm install -g netlify-cli" >&2
  exit 69
}

netlify deploy --dir "$SOURCE" --allow-anonymous
