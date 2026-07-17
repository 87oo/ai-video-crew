---
name: breakdown-video
description: |
  WHAT:爆款视频拆解团队(多 Agent)。输入一个本地视频文件,自动抽关键帧 → 视觉模型逐帧分析镜头语言(景别/运镜/转场/色调/节奏)→ 转录口播文案 → 输出完整爆款拆解报告 + 可落地仿拍建议。
  WHEN:用户说「拆解这个视频」「分析这条爆款」「视频拆镜」「仿拍分析」「breakdown video」「这个视频怎么拍的」时激活。
  NOT FOR:视频生成(用 byted-ark-seedance)/ 文生图(用 byted-ark-seedream)/ 视频剪辑。
argument-hint: "<视频文件路径> [--interval 2] [--max-frames 15] [--transcribe]"
allowed-tools:
  - Read
  - Bash
  - Write
  - Glob
  - Agent
  - mcp__4_5v_mcp__analyze_image  # 可选:Z.ai/中转环境有;真 Claude Code 没有,退回 Read 直接看图
---

# 爆款视频拆解团队 / Breakdown Video

## 概述
多角色 Agent 团队(灵感来自苍何的「爆款视频拆解团队」):
- **阿爆(本 skill / 团长)**:抽帧 → 逐帧看图(**自适应:有 analyze_image 用它,无则 Read 直接看**)→ 整合报告
- **小淼(video-shot-analyzer)**:镜头语言分析师,接收阿爆的"帧描述文本" → 综合分析景别/运镜/节奏 → 出镜头表 + 仿拍建议

> ⚠️ 架构要点:**看图在主线程(阿爆)做**。实测自定义 subagent 拿不到 MCP 工具(analyze_image 不注入显式 tools 白名单的 subagent),所以"阿爆看图、小淼分析"——这是正确分工,不是降级。

## 前置依赖
- **opencv-python**(抽帧):已装(4.12.0.88),wheel 内置 ffmpeg 编解码,**无需系统装 ffmpeg**。缺则 `pip install opencv-python`
- **视觉(自适应,二选一)**:
  - 有 `mcp__4_5v_mcp__analyze_image`(Z.ai/中转环境,glm 不直接看图)→ 用它看图
  - 没有(真 Claude Code,Read 原生注入视觉)→ Read 读图直接看
  - 两者都产出"帧描述文本",后续流程一样
- (可选)**HyperFrames transcribe**(口播转录):`npx hyperframes transcribe <file> --language zh`

## 工作流

### 1. 接收 & 校验视频
- 确认本地文件存在(`ls`/Glob)。MVP 只支持**本地视频文件**;给 URL 则提示"请先下载到本地,v2 支持自动下载"。

### 2. opencv 抽关键帧
Write `.breakdown-frames/extract.py` 并运行:
```python
import cv2, os, sys
video, interval, maxf = sys.argv[1], float(sys.argv[2]) if len(sys.argv)>2 else 2.0, int(sys.argv[3]) if len(sys.argv)>3 else 15
os.makedirs('.breakdown-frames', exist_ok=True)
cap = cv2.VideoCapture(video)
fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
duration = total / fps if fps else 0
i, t, stamps = 0, 0.0, []
while t < duration and i < maxf:
    cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, fr = cap.read()
    if ok:
        cv2.imwrite(f'.breakdown-frames/frame_{i:04d}.jpg', fr)
        stamps.append((i, round(t, 1)))
        i += 1
    t += interval
cap.release()
print(f'DURATION={duration:.1f}s FPS={fps:.1f} EXTRACTED={i}')
for idx, ts in stamps:
    print(f'frame_{idx:04d}.jpg|{ts}s')
```
运行:`python .breakdown-frames/extract.py "<视频>" 2 15`
- `--interval` 默认 `2`(每 2 秒一帧);短视频可用 `1`。
- 帧数超 `--max-frames`(默认 15)时加大 interval 重抽。

### 3. 逐帧看图(关键步骤,自适应)
先看你(主线程)工具列表有没有 `mcp__4_5v_mcp__analyze_image`,选一种:

**方式 A —— 有 analyze_image(Z.ai/中转环境)**
对每帧:a. Read 读 jpg → 拿 CDN URL;b. 调 `mcp__4_5v_mcp__analyze_image`(imageSource=URL),prompt 识别景别/主体/色调/构图/文字;c. 收集描述文本。

**方式 B —— 无 analyze_image(真 Claude Code)**
对每帧:直接 Read 读 jpg → 图会注入视觉,你直接看 → 自己写描述(景别/主体/色调/构图/文字)。

两种方式都产出"帧描述文本",后续流程不变。

> ⚠️ 看图在主线程(阿爆)做。小淼(subagent)拿不到 MCP 工具,所以阿爆看图、把描述传给小淼分析。

### 4. spawn 小淼做镜头语言综合分析
把"帧描述列表"(文本,不是 URL)传给小淼:
```
Agent(subagent_type="video-shot-analyzer", prompt="""
<frame_descriptions>
frame_0 | 0s | 特写;红色方块;暖色调高饱和;文字 SHOT1-CLOSEUP
frame_2 | 4s | 特写;蓝色方块;冷色调高饱和;文字 SHOT3-TILT
...
</frame_descriptions>
请综合分析这条视频的镜头语言,返回镜头表 + 视觉风格小结 + 仿拍建议。
""")
```
小淼返回镜头拆解表(景别/运镜/转场/色调)+ 风格小结 + 仿拍建议。

### 5. (可选)转录口播文案
若要 `--transcribe`:`npx hyperframes transcribe "<视频>" --language zh -o .breakdown-frames/transcript.srt`
失败则标注"转录失败,口播留空"。

### 6. 整合拆解报告
阿爆把【镜头表 + 视觉风格 + 口播文案】写成 `breakdown-report.md`:
```markdown
# 视频拆解报告:<文件名>
## 基本信息(时长/帧率/抽帧数/平台)
## 逐镜头拆解(小淼的镜头表)
## 视觉风格分析(小淼的小结)
## 口播文案(transcript,若有)
## 剪辑节奏 & 仿拍建议(阿爆综合 + 小淼建议)
```

## 降级处理
- **小淼 spawn 失败**:阿爆主线程直接做综合分析(有 LLM 能力),不依赖小淼。
- **opencv 没装**:`pip install opencv-python`(国内镜像快)。
- **视频过长**(>5 分钟):加大 interval 或分段。

## MVP 限制(后续版本补)
- ❌ 不支持 URL 自动下载(要本地文件)→ v2 加 yt-dlp/playwright 三层降级
- ❌ 不支持平台路由(抖音/B站/视频号)→ v2 加
- ⚠️ 运镜分析基于连续帧推断,不如真视频理解模型精确
- ⚠️ 抽帧数受 token 上限约束,长视频需加大 interval
