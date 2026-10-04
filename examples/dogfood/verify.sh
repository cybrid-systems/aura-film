#!/usr/bin/env bash
# Exit 0 iff candidate prints the cave/here clocks and defines film:clock-ms.
set -euo pipefail
CAND="${1:-}"
if [[ -z "$CAND" || ! -f "$CAND" ]]; then
  echo "usage: verify.sh <candidate.aura>" >&2
  exit 2
fi

src="$(cat "$CAND")"
if ! printf '%s\n' "$src" | grep -qE '\(define[[:space:]]+\(film:clock-ms([[:space:]]|\))'; then
  echo "verify fail: missing (define (film:clock-ms …)" >&2
  exit 1
fi

AURA_SRC="${AURA_SRC:-/workspace/aura-grok}"
IMG="ghcr.io/cybrid-systems/dev:v1.0.9"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

run_aura() {
  local cand="$1"
  if [[ -n "${AURA_BIN:-}" && -x "${AURA_BIN}" ]] && "${AURA_BIN}" -e '(display 1)' >/dev/null 2>&1; then
    AURA_SANDBOX="${AURA_SANDBOX:-off}" AURA_PIPELINE_STRICT="${AURA_PIPELINE_STRICT:-0}" \
      AURA_PATH="${AURA_PATH:-$AURA_SRC/lib}" \
      "$AURA_BIN" "$cand" 2>&1 || true
    return
  fi
  if docker info >/dev/null 2>&1; then
    DOCKER=(docker)
  elif sudo docker info >/dev/null 2>&1; then
    DOCKER=(sudo docker)
  else
    echo "verify fail: no usable AURA_BIN and no docker" >&2
    exit 2
  fi
  local abs
  abs="$(cd "$(dirname "$cand")" && pwd)/$(basename "$cand")"
  "${DOCKER[@]}" run --rm --entrypoint /usr/local/bin/gosu \
    -v "$AURA_SRC":/workspace/aura-grok \
    -v "$ROOT":/workspace/aura-film \
    -v "$abs":/tmp/candidate.aura:ro \
    -w /workspace/aura-film \
    -e AURA_PATH=/workspace/aura-grok/lib \
    -e AURA_PIPELINE_STRICT=0 \
    -e AURA_SANDBOX=off \
    "$IMG" \
    dev /workspace/aura-grok/build/aura /tmp/candidate.aura 2>&1 || true
}

out="$(run_aura "$CAND")"
printf '%s\n' "$out"
ok=1
printf '%s\n' "$out" | grep -q 'BEAT id=cave clock=23:40:00.000' || ok=0
printf '%s\n' "$out" | grep -q 'BEAT id=here clock=00:00:00.000' || ok=0
printf '%s\n' "$out" | grep -q 'YOU ARE HERE' || ok=0
printf '%s\n' "$out" | grep -q 'FILM_M0_OK' || ok=0
if printf '%s\n' "$out" | grep -qiE '\berror:|\bunbound variable\b'; then
  ok=0
fi
if [[ "$ok" -eq 1 ]]; then
  echo "verify ok cave=23:40 YOU ARE HERE FILM_M0_OK"
  exit 0
fi
echo "verify fail (expected cave 23:40 / here 00:00 / YOU ARE HERE / FILM_M0_OK + film:clock-ms)" >&2
exit 1
