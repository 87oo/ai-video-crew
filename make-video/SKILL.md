---
name: make-video
description: |
  WHAT:视频生成团队(多 Agent,仿苍何)。输入一句话主题,自动策划脚本分镜 → 用 HyperFrames 渲染成 MP4 视频(标题+要点+动画)。
  WHEN:用户说「做个视频」「生成视频」「把 XX 做成视频」「make video」「生成一段宣传片」时激活。
  NOT FOR:视频拆解(用 breakdown-video)/ AI 视频素材生成(用 byted-ark-seedance)。
argument-hint: "<主题> [--duration 15] [--style tech]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Agent
---

# 视频生成团队 / Make Video

## 概述
多角色 Agent 团队(灵感来自苍何的「视频生成团队」):
- **凌导(本 skill / 团长)**:接收主题 → spawn 灵枢策划 → spawn 灵映渲染 → 交付 MP4
- **灵枢(video-planner)**:内容策划,主题 → 脚本分镜
- **灵映(video-producer)**:视频制作,分镜 → HyperFrames composition → MP4

## 前置依赖(已全部就绪)
- **HyperFrames CLI**(`npx hyperframes`,v0.7.61)✅
- **Chrome 引擎**(首次 render 自动下载,已缓存)✅
- **ffmpeg**(已固化到 `D:\miniconda3\Scripts`,全局 PATH)✅

## 工作流
1. 接收主题(如"AI 周报"/"产品介绍")+ 可选时长/风格,确定输出目录(默认 `~/Video-Output/<主题>/`)
2. **spawn 灵枢**:主题 → 分镜 JSON
   ```
   Agent(subagent_type="video-planner", prompt="<brief>主题:XXX 时长:Ys 风格:ZZZ</brief> 出分镜JSON")
   ```
3. **spawn 灵映**:分镜 → 渲染 MP4
   ```
   Agent(subagent_type="video-producer", prompt="<shots>分镜JSON</shots> <output>输出目录</output>")
   ```
4. 把灵映返回的 MP4 路径告诉用户,并说明可预览

## MVP 限制(后续版本补)
- ❌ 灵阅(搜热点)未做 → 用户直接给主题
- ❌ 发布未做 → 只出到 MP4(云手机闭源,发布手动)
- ⚠️ TTS 配音为可选步骤(hyperframes tts);MVP 默认做**无声文字动画视频**,加配音时让灵映走 tts
- ⚠️ 视觉素材(图片/视频片段)未集成 → MVP 用纯 CSS/文字+动画
