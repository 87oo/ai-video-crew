# make-video —— AI 视频生成 skill(Claude Code)

仿苍何「视频生成团队」:**一句话主题 → 自动策划分镜 → HyperFrames 渲染成带配音的 MP4**。

## 多 Agent 分工
- **凌导**(`make-video` skill 主):接收主题、调度、整合交付
- **灵枢**(`video-planner`):内容策划,输出分镜 + 旁白文案
- **灵映**(`video-producer`):HyperFrames 渲染画面 + TTS 配音

## TTS 双后端(自动切换,对用户无感)

| 环境 | 后端 | 说明 |
|---|---|---|
| 设了 `ARK_API_KEY` | **豆包** doubao-seed-tts-2.0 | 中文好,需火山方舟 Agent Plan |
| 没设 | **Kokoro**(HyperFrames 自带) | 本地免费开源,中文音色 `zf_xiaobei` |

- 想用豆包:`setx ARK_API_KEY "ark-..."`(Windows)后重开终端
- 不设就自动用 Kokoro(开源默认,零成本)

## 依赖

| 依赖 | 安装 | 用途 |
|---|---|---|
| HyperFrames | `npx hyperframes`(首次自动下 Chrome) | 渲染 HTML→MP4 |
| ffmpeg + ffprobe | `conda install -c conda-forge ffmpeg` | 编码 + probe 时长 |
| kokoro-onnx + soundfile | `pip install kokoro-onnx soundfile` | Kokoro 后端(可选,用豆包可不装) |

> ⚠️ Kokoro 首次运行会下载 voice data(~27MB,需能访问 GitHub);网络不通时改用豆包。

## 安装

1. `SKILL.md` → `~/.claude/skills/make-video/SKILL.md`
2. `video-planner.md`、`video-producer.md` → `~/.claude/agents/`
3. `scripts/`(tts.py, doubao_tts.py)→ `~/.claude/skills/make-video/scripts/`
4. 重启 Claude Code(让 agent 注册)
5. 用法:对话里说「做个视频,主题:XXX,15秒」

## 安全

- `ARK_API_KEY` 走环境变量,**绝不进仓库**;`doubao_tts.py` 只读环境变量,代码里不含 key。
- 推 GitHub 前确认 `.gitignore` 排除任何含 key 的文件。

## MVP 限制
- 无 URL 自动下载(要本地素材)、无发布、无 AI 生图/视频片段(画面是 HTML 渲染)。
- 灵阅(搜热点)、视觉素材、发布等是 v2 扩展点。
