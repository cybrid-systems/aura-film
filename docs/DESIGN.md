# aura-film — design (Aura-native)

The product is a live Soft FlatAST world: the timeline, the clock, the
beats, the captions, the music parameters, and the scene graph are Soft
definitions in one Aura process. A thin program blits `SNAP` frames. It is
not the film.

This is the same loop aura-tetris and aura-go already play. Soft emits a
snapshot. The viewport paints it. Later, keys come back as `INPUT` lines,
and a cut strategy is swapped with `hot-strategy:swap!` /
`hot-strategy:heal!`. M0 stops before that swap. The clock the swap will
own is already Soft.

Code-as-造物, not diffusion. No predicted pixels, no stock plate, no
licensed score.

## One sentence

Drawing a clock is hygiene. The film is: Soft owns the day, a cut can be
hot-swapped, worldlines can race alternate shots, a proposal is gated
before it sticks, and the blit never invents a beat.

## North star

From the Fable / 「人类发明史压缩成 24 小时」 piece, adapted to Aura
dogfood, not to a video model:

1. **FlatAST owns the reel.** Year, clock, beat id, caption, tone, tempo,
   glyph, and whether the caption is shown are workspace data.
2. **Blit is thin.** Python (M0) or C (later) reads `SNAP v1` … `END` and
   paints. It does not store the invention table. ffmpeg only packs frames
   and a tone synthesized from `TONE`.
3. **Hot-strategy cuts (M1).** A body `(lambda (on-beat scene) …)` returns
   a number. `swap!` / `heal!` change the cut without retconning the clock.
4. **Worldline race (M1).** Several cuts score the same playhead.
   `fiber_live` is stamped only when the fibers actually join. Otherwise
   `host-sequential`. Never a fake fiber line.
5. **EXPLAIN.** `mid` and `reason` say why that cut won (`on_beat`,
   `hold_scene`, later `gate_reject` / `heal`). The blit does not invent
   the reason.
6. **Propose (later).** A host script may write a lambda. Soft gates it.
   HTTP stays outside Soft. No API key in this repo, no key on stdout.

M0 is the clock plus an honest two-cut select on the caller.

## Aura loop

```
(seek year) → soft/film/world.aura
                 │  clock-ms, active beat, cut score
                 ▼
              stdout: SNAP v1 … END
                 │  CLOCK, BEAT, SCENE, CAPTION, TONE, TEMPO,
                 │  PROGRESS, GLYPH, CUT, EXPLAIN, WORLD
                 ▼
              scripts/blit_snap.py draws PPM. ffmpeg muxes.
              It does not choose the next year.
```

M0's driver is `soft/film/m0_smoke.aura`. `export_frames.aura` is the same
seek, twelve times, for the short picture. Logs that are not SNAP stay
outside the `SNAP`/`END` pair so the pipe stays parseable.

## Clock law

```
now          = 2026
day          = 86,400,000 ms
span         = 3,240,000 years
ms_before    = years_ago * 80 / 3      ; integer quotient
clock_ms     = 0 if ms_before >= day else day - ms_before
```

`80/3` is exactly 1,200,000 ms per 45,000 years, which is 20 minutes. Cave
art at year `2026 - 45000 = -42974` is therefore `23:40:00.000`. Paper
(105 CE), rail (1825), and the personal computer (1977) are not entered as
clock strings. See `docs/m0.md` for the integer results next to the
article's rounded subseconds.

The start of the day and `YOU ARE HERE` both display `00:00:00.000`. SNAP
separates them: progress `0` versus `1000000`, and `AT_NOW` is 1 only at
year 2026. The blit reads those fields. It does not guess.

Tone is a parameter. `0` means silence (the long wilderness). The wav in
`render.sh` is a sine at `TONE` hertz, or zeros. It is not a recording.

## Soft vs blit

| Soft owns | Blit may do |
|-----------|-------------|
| year → clock milliseconds | PPM pixels of `CLOCK` and the hand angle from `H` `M` `S` `SUBMS` |
| beat id, scene, glyph name | a procedural icon for that glyph name |
| caption text, `SHOW_CAPTION` | draw the caption string if the flag is 1 |
| `TONE`, `TEMPO` | silence or a sine at `TONE` |
| cut id, score, reason | nothing about which cut won |
| `PROGRESS`, `AT_NOW` | the bar and the "AT NOW" mark |

The blit uppercases the beat id only so its tiny Latin glyphs can draw it.
The id in the SNAP is still the Soft string.

## Cuts in M0

Two pure scores, both called on the evaluating fiber:

| cut | score |
|-----|-------|
| austere | 3 on an exact beat year, else 0 |
| dense | 1 always |

Higher wins. On a beat, austere wins (`reason=on_beat`) and the caption is
shown. Between beats, dense wins (`reason=hold_scene`) and the previous
scene's caption is held. `WORLD line=host-sequential`. There is no
`fiber:spawn` in this file. Saying otherwise would be the fake this design
exists to forbid.

## Soft ≠ Restricted

| | This product | Not this product |
|--|----------------|------------------|
| World | FlatAST workspace defines | A native plugin / `.so` region |
| Swap (M1) | `std/hot-strategy` | `std/hot-update` (`aot:reload`) |
| Heal (M1) | `hot-strategy:heal!` | `std/heal` mid-reel surgery |
| Sandbox | **off** when a future seed uses `set-code` | Restricted mode as the play loop |
| Fibers | honest `fiber_live` or `host-sequential` | a label with no join |
| Picture | procedural blit of SNAP | diffusion / video-model pixels |

M0 does not register a hot-strategy and does not spawn a fiber.

## M1 sketch — SNAP pipe + strategy

The pipe already exists (`SNAP v1` … `END`). M1 does not teach the blit
new history. It adds:

1. **Register `film:cut-fn`.** Seed once with `set-code` (`AURA_SANDBOX=off`,
   same honesty as aura-tetris). After `hot-strategy:register!`, only
   `swap!` / `heal!`.
2. **Gate.** Body must look like `(lambda (on-beat scene) …)` and return a
   number. Reject text that mentions `set!`, `display`, `mutate:`, `eval`,
   `load`, `shell`, or `http`. `mutate:boundary-safe?` and
   `mutate:quota-ok?` must hold. Probe `(film:cut-fn 1 1)`. A non-number
   `heal!`s. EXPLAIN reasons: `gate_reject`, `swap`, `heal`.
3. **Race.** Four cuts on the same playhead: austere, dense, silent-until-rail,
   end-weighted. Build the candidate list on the caller. Spawn only if it
   is a real join. Stamp `fiber_live` only when four distinct ids join to
   scores. Otherwise run the same folds on the caller and stamp
   `host-sequential`. Do not upgrade the label by hand.
4. **SNAP grows, the blit does not.** Extra lines: `GHOST` (the cuts that
   lost), `WINNER`, `WORLD line=`. The Python (or a later `c/play.c`) still
   only blits. `INPUT seek <year>` and `INPUT race` are the verbs. C must
   not write `*play-year*`.
5. **Propose, gated.** Host Python writes a lambda file. Soft reads it.
   No key in the repo. If the key is absent, smoke prints a skip line and
   the fixture half still passes. The second day (years after 2026) is
   imagination, flagged `IMAGINED 1`, not a forecast. M0 does not enter it.

`ast:restore` is a whole-tree snapshot. A failed probe must not rewind the
clock. Prefer rebinding the previous cut body, the same lesson as the Go
dual slots.

## Non-goals

- Not a diffusion film and not a shot-for-shot copy of someone else's
  rendered short. The clock law and the glyphs are ours.
- Not a plugin moat. No AOT region whose point is to hide the timeline in C.
- Not a second timeline inside the blit "so the picture still works if
  Soft is slow."
- Not a claim that M0 fibers ran. They did not.
- Not MiniMax-in-process. No key file, no token, no endpoint secret.

## Files

| Path | Role |
|------|------|
| `soft/film/world.aura` | clock, beats, scene graph, cut select, SNAP |
| `soft/film/m0_smoke.aura` | `FILM_M0_OK` |
| `soft/film/export_frames.aura` | frame export |
| `scripts/smoke_soft.sh` | Docker Soft smoke |
| `scripts/render.sh` | SNAP → PPM → optional mp4 |
| `scripts/blit_snap.py` | the thin blit |
| `c/README.md` | why there is no `play.c` yet |
| `examples/dogfood/` | aura-build exercise for `film:clock-ms` |

## 短中文

产品是活的 Soft 世界，不是又一个 C 时间轴，也不是扩散视频。M0 把发明史压进
24 小时：`years_ago * 80 / 3` 毫秒，洞穴壁画因此落在 23:40:00.000。字幕、
音高、场景名都在 SNAP 里。Python 只画。节拍上 austere，节拍之间 dense，印
`host-sequential`。M1 再加热策略门、四条世界线、`EXPLAIN`。没有真 join 就不印
fiber_live。Soft 不是 Restricted，也不是 AOT。密钥不进仓库。
