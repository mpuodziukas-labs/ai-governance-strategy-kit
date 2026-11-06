#!/usr/bin/env bash
# Usage: bash scripts/verify.sh [--selftest]
set -euo pipefail
cd "$(dirname "$0")/.."

if [ "${1:-}" = "--selftest" ]; then
  exec python3 -m govkit.selftest
fi

python3 -m pytest -q

tmp="build"
mkdir -p "$tmp"
python3 -m govkit.generate "$tmp/a" > "$tmp/names"
python3 -m govkit.generate "$tmp/b" > /dev/null
count="$(wc -l < "$tmp/names" | tr -d ' ')"
[ "$count" -ge 7 ] || { echo "RED: only $count generated files"; exit 1; }
while IFS= read -r name; do
  [ -s "$tmp/a/$name" ] || { echo "RED: empty $name"; exit 1; }
  cmp "$tmp/a/$name" "$tmp/b/$name" || { echo "RED: $name differs between runs"; exit 1; }
done < "$tmp/names"
echo "byte-identical: $count files"

mkdir -p out
while IFS= read -r name; do
  if [ "$name" = "ROADMAP.md" ]; then cp "$tmp/a/$name" ROADMAP.md; else cp "$tmp/a/$name" "out/$name"; fi
done < "$tmp/names"

python3 -m govkit.selftest

shellcheck scripts/verify.sh
echo "shellcheck: 0"

pat="$(printf '/Use''rs/|/ho''me/|[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}|\xe2\x80\x94')"
if grep -rIEn --exclude-dir=.git --exclude-dir=__pycache__ --exclude-dir=.pytest_cache -e "$pat" . ; then
  echo "RED: leak pattern found"; exit 1
fi
echo "leak grep: 0"

echo GREEN
