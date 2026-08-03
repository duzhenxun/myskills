# Storyboard

**Format:** 1920x1080
**Duration:** 20 seconds
**Audio:** Chinese voiceover if generated, otherwise silent visual promo with readable kinetic titles
**VO direction:** Warm, bright, mobile-app confidence; relaxed Chinese delivery with short pauses
**Style basis:** DESIGN.md, captured Inke homepage, captured assets

## Asset Audit

| Asset | Type | Assign to Beat | Role |
| --- | --- | --- | --- |
| `capture/assets/mtu5mjiwnzi4ody5nym5mdejcg5n.png` | App icon | Beat 1, Beat 4 | Brand opener and closing logo |
| `capture/assets/mtywndyzmzmzndyznimgndijcg5n.png` | Hero decorative strip | Beat 1, Beat 4 | Floating teal shapes, rings, crown |
| `capture/screenshots/scroll-000.png` | Website hero screenshot | Beat 1, Beat 2 | Hero stage reference, page world |
| `capture/screenshots/scroll-063.png` | Story/live section screenshot | Beat 3 | Story and live discovery proof |
| `capture/assets/scaleimage.jpg` | Story image | Beat 3 | Editorial story card detail |
| `capture/assets/hero-1.jpg` | Executive/story image | Beat 3 | Editorial story card detail |
| `capture/assets/download-code.png` | QR code | Beat 4 | Mobile download CTA |
| `capture/assets/mtu4odk5mzmwntiyosm0ndqjcg5n.png` | Badge image | Beat 2 | Small proof/detail accent |
| `capture/assets/mtywndyzmjiwmzm5nim5mzmjcg5n.png` | QR code duplicate | SKIP | Duplicate QR image; use `download-code.png` instead |

## Beat 1 — Hook: The Room Opens (0.00-5.00s)

**VO cue:** "直播不只是观看。"

**Concept:** The video opens inside the bright Inke world rather than on a blank title card. The app icon pops forward, teal rings drift behind it, and the captured homepage hero expands into a living stage. It should feel like a mobile live room becoming a social space.

**Visual description:** A white canvas fills the frame. The teal app icon floats near center-left, surrounded by soft aqua rings and tiny dots borrowed from the captured hero decorations. A large rounded browser-stage panel slides into the center using `scroll-000.png`, cropped to emphasize the hero module rather than the browser chrome. The headline "直播不只是观看" lands in big PingFang type on the right, with a thin teal underline drawing itself underneath.

**Mood direction:** Bright app launch energy; clean, friendly, rounded, lightly playful.

**Techniques:** Per-word kinetic typography, SVG path drawing underline, CSS 3D card reveal, deterministic floating particles.

**Transition:** Velocity-matched upward into Beat 2.

**Depth layers:** BG white plus teal glow; MG captured hero screenshot panel; FG app icon, headline, floating dots.

## Beat 2 — Live: A Room Is Happening (5.00-10.00s)

**VO cue:** "在映客，打开一个直播间，就能遇见正在发生的故事。"

**Concept:** The viewer moves closer to the live-room interface. Instead of presenting a static screenshot, the promo reconstructs the captured live module into a layered card system with the same labels: "映客号: 774870442", streamer names, "+ 关注", and "手机客户端下载安装".

**Visual description:** A large dark rounded live-stage card occupies the left two-thirds of the frame. On it, the `scroll-000.png` hero area slowly zooms as a soft overlay makes it feel like a live preview. Three stacked thumbnail cards cascade down the right side with names from the capture: "提米", "一涵呀", "happy". A small QR chip sits in the lower-left of the stage as a secondary download cue. Teal pills and orange badge accents match the captured UI.

**Mood direction:** Immediate, social, in-progress; a live room you can enter.

**Assets:** `scroll-000.png`, `download-code.png`, `mtu5mjiwnzi4ody5nym5mdejcg5n.png`, `mtu4odk5mzmwntiyosm0ndqjcg5n.png`.

**Techniques:** CSS 3D stacked cards, SVG connector pulse, subtle Ken Burns on screenshot, counter-style typing for the Inke ID.

**Transition:** Blur-through into Beat 3.

**Depth layers:** BG white and light panel texture; MG live-stage card; FG stacked streamer cards and QR chip.

## Beat 3 — Discover: Stories And People (10.00-15.00s)

**VO cue:** "看主播，刷故事，发现热点内容。"

**Concept:** The page scroll becomes a discovery wall. The story module and live grid spread into a fast, editorial montage that shows Inke as both entertainment and content discovery.

**Visual description:** `scroll-063.png` sweeps in as a large tilted page slice. Individual story cards using `scaleimage.jpg` and `hero-1.jpg` lift off from the page into foreground media tiles. Chinese labels from the capture appear as short tags: "直播故事", "直播", "热点内容". A teal star icon draws itself beside the title and small dot particles drift between cards.

**Mood direction:** Browsing, discovering, scrolling; energetic but still clean.

**Assets:** `scroll-063.png`, `scaleimage.jpg`, `hero-1.jpg`, `mtywndyzmzmzndyznimgndijcg5n.png`.

**Techniques:** Scroll reveal, CSS 3D image cards, per-word typography, SVG icon path drawing.

**Transition:** Cinematic zoom into the QR/app icon CTA.

**Depth layers:** BG white; MG captured page slice; FG floating story cards and labels.

## Beat 4 — CTA: Take It With You (15.00-20.00s)

**VO cue:** "扫码下载映客，把下一次精彩，带到手机里。"

**Concept:** The final beat resolves from discovery into action. The app icon and QR code become the two anchors: brand and download.

**Visual description:** The decorative strip from the hero becomes a full-width soft background with teal rings and crown detail. The Inke app icon lands large on the left inside a rounded phone-like tile. The QR code appears on the right in a clean card labeled "手机客户端下载安装". The final line "看直播，玩直播，尽在映客" locks up across the center with a teal pill reading "立即体验".

**Mood direction:** Clear, upbeat, app-store CTA energy without looking like a hard sell.

**Assets:** `mtu5mjiwnzi4ody5nym5mdejcg5n.png`, `download-code.png`, `mtywndyzmzmzndyznimgndijcg5n.png`.

**Techniques:** Logo pulse, QR card reveal, SVG ring drawing, kinetic CTA pill.

**Transition:** Final soft fade to white in the last 0.4s.

**Depth layers:** BG decorative teal strip; MG app icon and QR card; FG final headline and CTA pill.

## Production Architecture

```text
inke-cn-promo/
├── index.html
├── DESIGN.md
├── SCRIPT.md
├── STORYBOARD.md
├── narration.txt
├── capture/
│   ├── screenshots/
│   ├── assets/
│   └── extracted/
└── compositions/
    ├── beat-1-hook.html
    ├── beat-2-live.html
    ├── beat-3-discover.html
    └── beat-4-cta.html
```
