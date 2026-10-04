#!/usr/bin/env bash
# Soft M0 smoke. Image ghcr.io/cybrid-systems/dev:v1.0.9, tip binary only.
# Never build_soft4132. Host GLIBC may be too old — always run Soft in docker.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/out"
bash "$ROOT/scripts/run_soft.sh" /workspace/aura-film/soft/film/m0_smoke.aura \
  >"$ROOT/out/m0_smoke.txt" 2>"$ROOT/out/m0_smoke.err"
cat "$ROOT/out/m0_smoke.txt"
if [[ -s "$ROOT/out/m0_smoke.err" ]]; then
  cat "$ROOT/out/m0_smoke.err" >&2
fi
fail=0
grep -q 'id=cave' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'clock=23:40:00.000' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'scene=hand' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'id=paper' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'clock=23:59:08.774' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'scene=paper' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'id=rail' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'clock=23:59:54.640' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'scene=rail' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'id=pc' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'clock=23:59:58.694' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'scene=terminal' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'id=here' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'clock=00:00:00.000' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'YOU ARE HERE' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'scene=sphere' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'cut=austere' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'reason=on_beat' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'cut=dense' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'reason=hold_scene' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'tone=0' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'WORLD line=host-sequential' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'SNAP v1' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q '^END$' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'CAVE_H=23 OK' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'CAVE_M=40 OK' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'PAPER_MS=774 OK' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'RAIL_MS=640 OK' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'PC_MS=694 OK' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'ORDER=1 OK' "$ROOT/out/m0_smoke.txt" || fail=1
grep -q 'FILM_M0_OK' "$ROOT/out/m0_smoke.txt" || fail=1
if grep -q 'FILM_M0_FAIL' "$ROOT/out/m0_smoke.txt"; then
  fail=1
fi
if grep -q 'fiber_live' "$ROOT/out/m0_smoke.txt" "$ROOT/out/m0_smoke.err"; then
  fail=1
fi
if grep -qiE 'error:|unbound variable' "$ROOT/out/m0_smoke.txt" "$ROOT/out/m0_smoke.err"; then
  fail=1
fi
if [[ "$fail" -ne 0 ]]; then
  echo "smoke_soft: FILM_M0_OK checks failed" >&2
  exit 1
fi
echo "smoke_soft: FILM_M0_OK"
