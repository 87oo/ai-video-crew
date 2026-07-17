# my-ai-video-crew

仿苍何「AI 视频团队」的 Claude Code skill 合集——**拆解学习** + **自动生成** 闭环。

## 两个 skill

### 🎬 make-video(生成)
一句话主题 → 自动策划分镜 → HyperFrames 渲染 + TTS 配音 → MP4。
- 多 Agent:凌导(调度)+ 灵枢(策划)+ 灵映(渲染)
- 双 TTS 后端:豆包(有 `ARK_API_KEY`)/ Kokoro(默认,免费开源)
- 详见 [`make-video/README.md`](make-video/README.md)

### 🔍 breakdown-video(拆解)
本地视频 → 抽关键帧 → 视觉分析镜头语言 → 拆解报告 + 仿拍建议。
- 多 Agent:阿爆(调度)+ 小淼(镜头分析)
- 自适应视觉:有 `analyze_image` 用它 / 无则 `Read` 直接看(真 Claude Code)
- 用途:学爆款、拆竞品、提取教程步骤

## 安装
1. `make-video/`、`breakdown-video/` → `~/.claude/skills/`
2. `agents/*.md` → `~/.claude/agents/`
3. 依赖:`conda install -c conda-forge ffmpeg` + `pip install opencv-python kokoro-onnx soundfile`
4. (可选,用豆包 TTS)`setx ARK_API_KEY "ark-..."` 后重开终端
5. 重启 Claude Code

## 用法
- 「做个视频,主题:XXX」→ make-video
- 「拆解 D:/xxx.mp4」→ breakdown-video

## 致谢
灵感来自 [苍何](https://mp.weixin.qq.com/s/zvFr25XDPORPVtYN4hS7Cw)的 AI 视频团队;渲染基于 [HyperFrames](https://github.com/heygen-com/hyperframes)(HeyGen 开源)。

## License
Apache License 2.0(与 HyperFrames 一致)—— 见 [LICENSE](LICENSE)。Copyright (c) 2026 87oo。

> `ARK_API_KEY` 走环境变量,绝不进仓库。推 GitHub 前确认无 key 硬编码。
