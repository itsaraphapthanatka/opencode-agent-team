# Marketing assets — opencode-agent-team

Brand and listing media for the Agensi skill [`opencode-agent-team`](https://agensi.io/skills/opencode-agent-team).

```
assets/
├─ logo/
│  ├─ logo.svg            # vector master (edit this)
│  ├─ logo-1024.png       # app-icon tile, hi-res (use for Agensi logo upload)
│  ├─ logo-512.png        # standard tile
│  ├─ logo-256.png        # favicon size
│  └─ logo-concepts.svg   # the 3 explored directions (A chosen)
├─ screenshots/           # 1600×1000, upload in order
│  ├─ 01-hero.png
│  ├─ 02-file-tree.png
│  ├─ 03-roles.png
│  ├─ 04-commands.png
│  ├─ 05-terminal.png
│  └─ 06-before-after.png
└─ DEMO-STORYBOARD.md      # ~70s demo video shot list + caption deck + VO script
```

## Brand
- **Logo:** orchestration hub — a central hex core with six agent nodes, one cyan "lead" node.
- **Palette:** dark slate tile (`#121826 → #090C14`), accent gradient cyan→indigo (`#22D3EE → #3B82F6 → #6366F1`).
- **Type:** Helvetica (headings), Menlo (code/terminal).

## Upload to Agensi
Media upload is login-gated, so do it from the dashboard:
1. **Logo:** https://agensi.io/dashboard/submit?media-upload=logo → upload `logo/logo-1024.png`.
2. **Screenshots:** https://agensi.io/dashboard/submit → screenshots field (max 6) → upload `screenshots/01…06` in order.
3. **Demo video:** record a ~70s screen capture following `DEMO-STORYBOARD.md`, host on YouTube/Vimeo, paste the link into `demo_video_url`.

## Regenerating
The PNGs were rendered from scripts kept with the session (Pillow for the logo and screenshots).
The logo master is `logo/logo.svg`; re-export at any size from there.
