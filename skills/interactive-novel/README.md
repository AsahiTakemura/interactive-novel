# 互动小说 · Codex 版本

上传或指定 `.epub`、`.txt`、`.pdf`、`.md` 书籍后，用 `$interactive-novel` 开始。先了解无剧透背景与可选角色，再通过选择进入主线、支线或平行时间线；输入 `C` 或自由文本可讨论当前选择。每轮叙述、角色对话及讨论保留原版的场景插画要求。

## Features

- **Branching Narratives** — Make choices that determine the story's outcome
- **Multiple Endings** — Different choices lead to different conclusions
- **Side Character Play** — Play as non-main characters with unique backstories
- **Parallel Timelines** — Wrong choices branch off into alternate storylines
- **Chat About This** — Pause and discuss your options before deciding
- **Scene Illustrations** — Generate one new image after each story or dialogue turn, including discussions, with consistent characters and no spoilers for future events or unchosen branches. Images and prompts stay in the user's project; the built-in image tool is the default.
- **Retrace** — Revisit choices and explore different paths

## 可选键盘菜单

菜单在交互终端中支持上下方向键、Enter 确认、Esc 取消。聊天中的普通文本仍支持编号和自由回复。

```text
python -X utf8 scripts/selector.py --title "选择角色" "主角" "配角" "讨论"
```

也可用 UTF-8 `options.json` 保留稳定选项 id：

```json
[
  {"id": "main", "label": "主角"},
  {"id": "side", "label": "配角"},
  {"id": "C", "label": "聊聊当前选择"}
]
```

```text
python -X utf8 scripts/selector.py --options-file options.json --output selection.json
```

确认后输出 `{"index": 2, "id": "side", "label": "配角"}` 并返回 `0`。取消返回 `2`，不会覆盖旧结果；调用者必须检查返回码，不能把旧结果当成新选择。错误返回 `1`。非交互终端退回编号输入，输入 `q` 取消。

Python 3.9 以上，无额外依赖，支持 Windows、macOS 和 Linux。故事文件、图像与选择结果保存在用户项目里。

## 来源

基于 [AsahiTakemura/interactive-novel 的 main 分支](https://github.com/AsahiTakemura/interactive-novel/tree/main)，原版为 Claude Code 制作。

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
