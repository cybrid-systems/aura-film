# Viewport

M0 has no C binary. `scripts/blit_snap.py` is the thin blit: it reads
`SNAP v1` … `END` and draws PPM frames. ffmpeg muxes those frames with a
tone built only from the SNAP `TONE` field (0 means silence).

The script does not choose the year, the beat, the caption, or the cut.
Those fields are already in the snapshot. A later `c/play.c` would be the
same contract: blit plus optional `INPUT seek`, never a second timeline.
