# opencode-agent-team — Demo video storyboard & script

A ~70-second screen-recording demo for the Agensi listing. Designed so the 6 marketplace
screenshots double as the title/section cards, keeping one visual system.

---

## Specs (what to record)
- **Length:** 60–75s (Agensi/YouTube loop-friendly). Hard cap 90s.
- **Resolution:** 1920×1080, 30fps. Record the OpenCode TUI/terminal at a **large font** (≈18–20pt) so text is readable on mobile.
- **Theme:** dark terminal (matches the brand: slate bg, cyan/blue accents).
- **Pace:** fast. Cut dead air and long model "thinking" pauses (speed-ramp them 4–8×).
- **Captions:** burn in the on-screen caption text below (big, bottom-center). Assume **no sound** — most marketplace viewers watch muted. Voiceover is optional.
- **Music:** low, minimal tech/lofi bed at ~15% volume (optional).
- **Export:** MP4 (H.264). Upload to YouTube/Vimeo (unlisted is fine) → paste the link into Agensi's `demo_video_url`.

---

## Shot list (scene by scene)

### 0:00–0:05 — Hook  *(title card)*
- **Screen:** `shot1-hero.png` held for ~2s, then hard-cut to a bare terminal in an empty-ish repo (`ls` shows `package.json  src/  tests/`).
- **Caption:** `Your repo has no team. Yet.`
- **VO (optional):** "This is any OpenCode project. Watch it become a software company."

### 0:05–0:16 — Invoke  *(the one command)*
- **Screen:** type the skill invocation and `init`. Show the skill start **exploring the repo** — scanning manifests, detecting the stack, reading test commands. Let a few real log lines fly by.
- **Caption:** `One command. It reads your real code first.`
- **VO:** "You run it once. Before writing anything, it explores your actual stack, tests and conventions."

### 0:16–0:26 — Choose the team  *(the 4 questions)*
- **Screen:** the `question` prompt with the 4 choices — profile (balanced), role set (core/full), language, docs location. Pick quickly.
- **Caption:** `Pick the team: core or the full 17-role org.`
- **VO:** "Answer four quick questions — how strong, how many roles, what language, where the docs live."

### 0:26–0:40 — Render  *(files appear)*
- **Screen:** the renderer runs — `WROTE .opencode/agents/…`, `WROTE .opencode/commands/…` scrolling, then `CHECK: frontmatter OK`. Cut to the file tree in the editor sidebar expanding (`.opencode/agents`, `commands`, `docs/`).
- **Caption:** `A whole team, written to disk.`
- **Insert (1s):** flash `shot2-tree.png` to make the structure legible.
- **VO:** "In one pass it writes every agent, every command, the docs, and a verified context file."

### 0:40–0:48 — The team  *(section card)*
- **Screen:** `shot3-team.png` (17 roles) ~2s, then `shot4-commands.png` (10 commands) ~2s.
- **Caption:** `17 specialists · 10 pipeline commands.`
- **VO:** "Seventeen specialists and ten pipeline commands — all grounded in your repo."

### 0:48–1:02 — Use it  *(the payoff in action)*
- **Screen:** run a real command, e.g. `/feature add JWT login` (or `/test-all`). Show the checkpoint summary, then **multiple subagents working in parallel** (dev, code-reviewer, security, tests). Speed-ramp the thinking; keep the moments where reports land.
- **Caption:** `/feature → PM, architect, devs, review, tests — in one flow.`
- **VO:** "Now you ship. One command runs the whole flow — product, design, build, review, security, tests, docs."

### 1:02–1:12 — Payoff & CTA  *(outro card)*
- **Screen:** `shot6-beforeafter.png` (bare repo → working org) ~3s, settle on `shot1-hero.png` with the logo.
- **Caption:** `From a bare repo to a working org. opencode-agent-team — on Agensi.`
- **VO:** "Same project, one command later: a working engineering org. Get it on Agensi."

---

## Caption deck (copy/paste, in order)
1. Your repo has no team. Yet.
2. One command. It reads your real code first.
3. Pick the team: core or the full 17-role org.
4. A whole team, written to disk.
5. 17 specialists · 10 pipeline commands.
6. /feature → PM, architect, devs, review, tests — in one flow.
7. From a bare repo to a working org.
8. opencode-agent-team — on Agensi.

## Full voiceover script (≈110 words, ~65s at a calm pace)
> This is any OpenCode project. Watch it become a software company.
> You run it once. Before writing anything, it explores your actual stack, tests and conventions.
> Answer four quick questions — how strong, how many roles, what language, where the docs live.
> In one pass it writes every agent, every command, the docs, and a verified context file that every agent reads first.
> Seventeen specialists and ten pipeline commands, all grounded in your repo.
> Now you ship. One command runs the whole flow — product, design, build, review, security, tests, docs.
> Same project, one command later: a working engineering org. Get it on Agensi.

---

## Production tips
- **Fake nothing that breaks:** record against a real small repo so the exploration/log lines are genuine. A FastAPI or Express starter works well and matches the demo text.
- **Readability first:** if a step's output is long, cut to the relevant 2–3 lines rather than the full scroll.
- **Keep the brand:** reuse the screenshot cards for transitions so the video and the listing feel like one product.
- **Thumbnail:** use `shot1-hero.png` (or a frame of the parallel agents working) as the video thumbnail.
- **Length discipline:** if you overrun, cut the voiceover before cutting the on-screen action — muted viewers rely on the captions.
