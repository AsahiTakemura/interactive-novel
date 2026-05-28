# Interactive Novel Engine

An interactive storytelling engine for Claude Code. Upload a book, choose your character, and experience the story through branching choices.

## Features

- **Branching Narratives** — Make choices that determine the story's outcome
- **Multiple Endings** — Different choices lead to different conclusions
- **Side Character Play** — Play as non-main characters with unique backstories
- **Parallel Timelines** — Wrong choices branch off into alternate storylines
- **Chat About This** — Pause and discuss your options before deciding
- **Retrace** — Revisit choices and explore different paths

## How to Use

Load this skill in Claude Code, then:

```
1. Trigger the skill with a book file (.epub / .txt / .pdf / .md)
2. Claude will read and understand the full story (no spoilers in output)
3. Review the character list and settings
4. Choose a character to play
5. Make choices that shape the story
```

## File Structure

```
interactive-novel/
├── SKILL.md          # Skill definition and flow instructions
├── scripts/
│   └── selector.py   # Interactive keyboard selector (optional)
└── README.md         # This file
```

## Example: Murder on the Orient Express

This skill was developed using Agatha Christie's *Murder on the Orient Express* as the first test case. It supports playing as either Poirot (the protagonist) or any of the 12 other passengers — each with their own backstory and branching path into the main plot.

## License

MIT
