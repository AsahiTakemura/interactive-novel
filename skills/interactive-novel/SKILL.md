---
name: interactive-novel
description: >
  Interactive novel engine for branching narrative adventures.
  TRIGGER when the user wants to upload a book and play through an interactive story with choices,
  multiple endings, and parallel timelines. Supports main-character and side-character perspectives,
  "chat about this" mode for discussing choices, and branching that leads to different endings.
  Use whenever the user provides a book file (.epub/.txt/.pdf/.md) and wants an interactive storytelling experience
  where they make choices that affect the story outcome.
---

# Interactive Novel Engine

## Overview

An interactive story engine that lets users upload a book, then play through the story as a character, making choices that affect the outcome. Supports branching narratives, side-character backstories, and a "chat about this" discussion mode.

## Workflow

### Phase 1: Load Book

1. Prompt the user for the book file path
2. Read the file and fully understand its content (plot, characters, settings, twists)
3. If the book is already loaded (from conversation context), confirm with the user

### Phase 2: Output Character & Story Info (No Spoilers)

After reading the book, present:

1. **Brief background** — Set the scene without revealing the murderer, the method, or major plot twists
2. **Character list** — A list of playable characters:
   - **Protagonist** (main character, follows the main storyline)
   - **Side characters** (each with a "branch backstory" that leads into the main plot)
3. **Possible endings** — List the available endings without revealing how to get them

Wait for the user to confirm before proceeding.

### Phase 3: Character Selection

Let the user pick a character to play.

### Phase 4: Storytelling

#### If the user plays the PROTAGONIST:
- Start from the beginning of the main story
- At key decision points, present choices
- Each choice affects which ending the user approaches

#### If the user plays a SIDE CHARACTER:
- **First: Branch Backstory** — Tell the story of who this character is and why they are on the train (their connection to the central events)
- **Set key choices** in this backstory phase:
  - **Correct choice** → enter the main storyline
  - **Wrong choice** → diverge into a parallel timeline
- **On wrong choice:**
  - Prompt the user: "You have strayed from the main timeline. Do you want to [R]etrace (go back) or continue to explore this parallel world?"
  - If they continue, the story proceeds in a new direction with its own ending(s)

### Phase 5: Choice Presentation

**CRITICAL RULE: Always provide full narrative context (dialogue, description, character thoughts) BEFORE presenting choices.**

By default, present choices as follows. Use the optional keyboard menu below when the user requests it:

```
──────────────────────────────────────────────────
  [1] "Dialogue or action option 1"

  [2] "Dialogue or action option 2"

  [3] "Dialogue or action option 3"

      [C] Chat about this
──────────────────────────────────────────────────
  Enter number | C to discuss
```

### Chat about this Mode

When the user types [C] or enters free text instead of a number:
1. User's input is their question/dialogue — respond directly as the narrator or characters in the story
2. After responding, re-present the same choice options so the user can continue

### Optional Keyboard Choices (Codex)

The bundled [selector](scripts/selector.py) supports ↑/↓ to move, Enter to confirm, and Esc to cancel in a visible interactive terminal. Chat Markdown does not implement this keyboard control. Keep numbered choices and free-text discussion available by default; use the terminal menu when the user asks for keyboard selection and can interact with that terminal.

1. Present the full narrative context first. For character selection or a story decision, write a UTF-8 JSON array of `{ "id": "stable-id", "label": "visible choice" }` objects into the current user project. Include `C` for discussion; include retrace only when there is a valid previous decision. Do not expose endings or hidden outcomes in labels.
2. Run the bundled selector in the user's visible interactive terminal, resolving `scripts/selector.py` from this skill directory:

   ```text
   python -X utf8 <skill-directory>/scripts/selector.py --title "请选择" --options-file <project>/options.json --output <project>/selection.json
   ```

3. Exit code `0` means the choice was confirmed. Read that newly written JSON (`index` is 1-based, plus `id` and `label`), check the id against the current options, then apply the choice. `C` opens discussion without advancing; retrace restores the previous decision.
4. Exit code `2` means canceled: preserve the current story position and do not read an old result file. Exit code `1` means an error: report it briefly and offer the same choices in chat. A terminal without arrow-key support falls back to numbered input; `q` cancels. Never infer a choice merely from the highlighted row or a canceled menu.

Do not run a hidden or pipe-only menu and wait for the user to interact with it. Keep options, results, books, and progress in the user's project, outside this skill repository.

### Per-Turn Scene Illustration

After each turn of story narration, character dialogue, or **Chat about this** discussion, generate and display **one new image** illustrating the scene just described. Narration and dialogue in the same response count as one turn, including a response that also presents choices. For discussion without a new scene, illustrate the current established scene without advancing the story.

- Base the image on events already narrated in the selected timeline. Do not reveal hidden clues, future events, endings, or unchosen branches.
- Keep character appearance, clothing, setting, period details, and visual style consistent across turns. Use established descriptions and prior images as continuity references when available.
- Use the built-in `image_gen` tool by default, following the imagegen skill when available. Generate a real new image for the turn; do not substitute a placeholder or reuse an old scene image.
- Save the prompt and final image in the current project's user deliverables area. If the tool saves elsewhere, copy the generated image into that area. Display the actual saved image inline using its absolute file path, after the narrative or discussion; keep the choice options available.
- If generation fails or the tool is unavailable, report that accurately and preserve the user's story position and choices. Do not claim success or silently switch to a CLI/API fallback; use that fallback only with the user's explicit agreement.
- Keep book text, session progress, prompts, generated images, and personal file paths out of the public skill repository.

### Phase 6: Branching & Endings

- Track the user's choices throughout the story
- Different endings are unlocked based on:
  - Key decisions made at critical nodes
  - Whether the user stayed on or diverged from the main timeline
  - The character they chose to play
- At the end, reveal which ending they reached and offer to play again as a different character

## Example: Orient Express (loaded)

### Background (Spoiler-Free)

**1930s Europe.** The Orient Express, a luxury train running from Istanbul to London, is carrying a diverse group of passengers through the Balkan mountains. A heavy snowstorm has stranded the train in the middle of the night. The next morning, a wealthy American businessman is found dead in his compartment — stabbed multiple times. The doors are locked from the inside. No one could have entered or left the train. The murderer is among the passengers.

### Characters

**Protagonist:**
- Hercule Poirot — Detective

**Side Characters:**
- Hector McQueen — Secretary
- Edward Masterman — Butler
- Mary Debenham — Governess
- Princess Dragomiroff — Aristocrat
- Hildegarde Schmidt — Maid
- Count Andrenyi — Diplomat
- Countess Andrenyi — Count's wife
- Colonel Arbuthnot — Military officer
- Cyrus Hardman — American detective
- Antonio Foscarelli — Car salesman
- Greta Ohlsson — Nurse
- Pierre Michel — Conductor
- Mrs. Hubbard — American tourist

## Skill Maintenance

Repository publishing requires the user's instruction. Playing a story does not authorize committing or uploading books, progress, images, or personal records.
