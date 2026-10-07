# 互动小说与芳乃语气 · Codex 版本

这个 `codex` 分支把两个 skill 放在同一个仓库：

| Skill | 用途 |
| --- | --- |
| `interactive-novel` | 基于书籍体验分支故事、角色选择、平行时间线和讨论；可选上下键与回车菜单 |
| `yoshino-tone` | 依据角色资料的芳乃中文表达、虚构对话及可携带记忆接续 |

## 安装

下载或克隆这个分支，使用 Python 3.9 以上运行：

```text
git clone --branch codex https://github.com/AsahiTakemura/interactive-novel.git
cd interactive-novel
python -X utf8 install.py --dry-run
python -X utf8 install.py
```

无需额外 Python 依赖。新安装默认进入 `$CODEX_HOME/skills`（未设置时为 `~/.codex/skills`）。如果 `~/.agents/skills/interactive-novel` 已存在，互动小说在原目录更新，避免重复安装。

安装器先校验 `SHA256SUMS.txt`，再备份已有 skill 到 Codex home 的 `backups/`。它保留已有记忆、故事进度、自定义文件和 `AGENTS.md`，只在缺少芳乃记忆文件时放入空白模板。安装不会自动启用默认角色语气。自定义位置可使用 `--codex-home` 和 `--agents-home`。

安装后，在下一轮 Codex 对话里调用 `$yoshino-tone` 或 `$interactive-novel`。想持续使用芳乃语气，直接告诉 Codex；安装包本身不修改全局会话指令。

## 上下键选择

互动小说保留聊天中的编号选择和自由讨论；用户要求键盘选择时，可在可见交互终端里用 ↑/↓ 移动、Enter 确认、Esc 取消。实际脚本位于安装后的 `interactive-novel/scripts/selector.py`：

```text
python -X utf8 skills/interactive-novel/scripts/selector.py --title "选择角色" "主角" "配角" "讨论"
```

带稳定 id 的文件输入与确认结果见 [互动小说说明](skills/interactive-novel/README.md)。普通聊天文本没有方向键菜单；终端不可用时继续使用聊天选择。取消不会推进故事。

## 文件与来源

```text
skills/
  interactive-novel/SKILL.md
  interactive-novel/scripts/selector.py
  yoshino-tone/SKILL.md
  yoshino-tone/agents/openai.yaml
  yoshino-tone/references/
memory-templates/
install.py
tests/
```

互动小说基于本仓库的 `main` 分支；芳乃语气来自作者的 `yoshino-companion` v5 包，保留角色模型、原创示例、来源说明和连续性约定。委派规则遵从当前用户偏好，不固定要求更高成本的模型。

公开包只含技能说明、程序、测试和空白记忆模板，不含书籍全文、原作脚本、个人记忆、对话、生成图片或本机路径。

运行验证：

```text
python -X utf8 -m unittest discover -s tests -v
```
