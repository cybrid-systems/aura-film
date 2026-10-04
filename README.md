# aura-film

Aura Film is a live Soft world. The 24-hour clock, the beats, the captions,
the music parameters, and the scene graph are a Soft FlatAST program. A thin
Python blit only paints `SNAP` frames. It does not pick the year.

M0 dogfood is 「人类发明史压缩成 24 小时」: cave art falls on **23:40:00.000**
because 45,000 years is 20 minutes under one integer law
(`years_ago * 80 / 3` milliseconds). Paper, rail, the personal computer, and
`YOU ARE HERE` (2026, midnight, progress full) are the same function.

Design: [`docs/DESIGN.md`](docs/DESIGN.md). Milestone: [`docs/m0.md`](docs/m0.md).
Repo: https://github.com/cybrid-systems/aura-film

Also an [aura-build](https://github.com/cybrid-systems/aura-build) dogfood
stub under `examples/dogfood/`.

This is code-as-造物, not a diffusion model. No stock footage, no library
music, no MiniMax key in the tree.

## Soft smoke

Image `ghcr.io/cybrid-systems/dev:v1.0.9`, Soft tip binary
`/workspace/aura-grok/build/aura` (host GLIBC is often too old — smoke always
runs Soft inside Docker with `--entrypoint /usr/local/bin/gosu`). Needs
`AURA_SANDBOX=off`.

```bash
bash scripts/smoke_soft.sh    # cave 23:40, paper, rail, PC, YOU ARE HERE → FILM_M0_OK
bash scripts/render.sh        # out/frames/*.ppm and, if ffmpeg exists, out/invention_24h.mp4
```

`render.sh` is about six seconds: twelve SNAP frames at 2 fps, plus a wav
whose frequency is the SNAP `TONE` (0 Hz is silence). The early day is silent.
The blit is `scripts/blit_snap.py`. It has no beat table.

Manual Soft run:

```bash
sudo docker run --rm --entrypoint /usr/local/bin/gosu \
  -v /workspace/aura-grok:/workspace/aura-grok \
  -v "$PWD":/workspace/aura-film \
  -w /workspace/aura-film \
  -e AURA_PATH=/workspace/aura-grok/lib \
  -e AURA_PIPELINE_STRICT=0 \
  -e AURA_SANDBOX=off \
  ghcr.io/cybrid-systems/dev:v1.0.9 \
  dev /workspace/aura-grok/build/aura /workspace/aura-film/soft/film/m0_smoke.aura
```

## Engine

| Path | Role |
|------|------|
| `soft/film/world.aura` | clock law, beats, captions, tone/tempo, scene, cut select, `SNAP v1` |
| `soft/film/m0_smoke.aura` | beat evidence → `FILM_M0_OK` |
| `soft/film/export_frames.aura` | twelve seeks, SNAP only, `FILM_EXPORT_OK` |
| `scripts/blit_snap.py` | PPM + wav from SNAP fields |
| `scripts/render.sh` | Soft export, then blit, then ffmpeg |
| `c/README.md` | no C binary in M0; same blit contract later |
| `examples/dogfood/` | GOAL / stub / golden / verify |

Cuts in M0 are two scores on the caller, not a hot-swap yet. On an exact
beat, austere wins (`reason=on_beat`). Between beats, dense holds the scene
(`reason=hold_scene`). The stamp is `WORLD line=host-sequential`. Soft does
not print a fiber-live line unless fibers actually join. They do not, in M0.

## Soft tip

- Binary: `/workspace/aura-grok/build/aura`
- Image: `ghcr.io/cybrid-systems/dev:v1.0.9`
- Env: `AURA_SANDBOX=off AURA_PIPELINE_STRICT=0 AURA_PATH=/workspace/aura-grok/lib`

Soft is not Restricted mode. M0 does not call `hot-strategy` and does not
stamp `fiber_live`.

License: Apache-2.0

---

# aura-film（中文）

活世界在 Soft：24 小时钟、节拍、字幕、配乐参数、场景图。Python 只把 `SNAP`
画成 PPM，ffmpeg 再包一层短片。画面不是扩散模型算出来的像素，也没有版权素材。

把人类发明史压进一天。整数律 `years_ago * 80 / 3` 毫秒：距 2026 年 4.5 万年
正好是午夜前 20 分钟，所以洞穴壁画在 **23:40:00.000**。造纸、铁路、个人电脑、
`YOU ARE HERE` 走同一条函数，不是另一张时刻表。文章里的 `23:59:09` /
`23:59:54.7` / `23:59:58.71` 是约数；M0 打印整数结果
（纸 `23:59:08.774`，铁路 `23:59:54.640`，电脑 `23:59:58.694`）。

```bash
bash scripts/smoke_soft.sh
bash scripts/render.sh    # out/invention_24h.mp4 ，约 6 秒，早期静音
```

节拍上 austere 赢（`on_beat`），节拍之间 dense 守住上一场景（`hold_scene`）。
印的是 `host-sequential`。没有真的 fiber join 就不印 fiber_live。
Soft 不是 Restricted，也不是 AOT 插件。仓库里没有 MiniMax 密钥。

镜像 `ghcr.io/cybrid-systems/dev:v1.0.9`，Soft 二进制 `/workspace/aura-grok/build/aura`。
仓库：https://github.com/cybrid-systems/aura-film
