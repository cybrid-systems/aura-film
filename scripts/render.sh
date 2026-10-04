#!/usr/bin/env bash
# Export a short procedural clock film from Soft SNAP blocks.
# Frames are PPM (no codec required). ffmpeg, when present, muxes a silent-or-tone mp4.
# Tone samples use only the SNAP TONE field. 0 Hz is silence. No library music.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/out/frames"
bash "$ROOT/scripts/run_soft.sh" /workspace/aura-film/soft/film/export_frames.aura \
  >"$ROOT/out/export.txt" 2>"$ROOT/out/export.err"
if [[ -s "$ROOT/out/export.err" ]]; then
  cat "$ROOT/out/export.err" >&2
fi
grep -q 'FILM_EXPORT_OK' "$ROOT/out/export.txt"
python3 "$ROOT/scripts/blit_snap.py" \
  "$ROOT/out/export.txt" \
  "$ROOT/out/frames" \
  "$ROOT/out/tones.wav"
frames=$(ls "$ROOT/out/frames"/f*.ppm 2>/dev/null | wc -l)
echo "render: ppm_frames=$frames"
if command -v ffmpeg >/dev/null 2>&1 && [[ "$frames" -gt 0 ]]; then
  ffmpeg -y -loglevel error -framerate 2 \
    -i "$ROOT/out/frames/f%03d.ppm" \
    -i "$ROOT/out/tones.wav" \
    -c:v libx264 -pix_fmt yuv420p -c:a aac -shortest \
    "$ROOT/out/invention_24h.mp4"
  echo "render: $ROOT/out/invention_24h.mp4"
else
  echo "render: ffmpeg missing or no frames; PPM sequence kept" >&2
fi
