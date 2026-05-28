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

Choices must be presented as follows:

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

## Git Management

This project is managed via git. To update:

```bash
git add .
git commit -m "description of changes"
git push
```

To revert to a previous version:

```bash
git log --oneline
git checkout <commit-id>
```