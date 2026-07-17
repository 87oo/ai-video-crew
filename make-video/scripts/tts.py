#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""统一 TTS 入口 —— 自动选后端,对调用方无感。

  - 设了环境变量 ARK_API_KEY → 豆包 doubao-seed-tts-2.0(中文好,需火山方舟 Agent Plan)
  - 没设                       → Kokoro(HyperFrames 自带,本地免费开源,中文音色 zf_xiaobei)

用法: python tts.py <文本> <输出.mp3> [音色]
音色可选:豆包传 doubao 音色(如 zh_female_gaolengyujie_uranus_bigtts),
         kokoro 传 kokoro 音色(如 zf_xiaobei);不传用各自默认。
"""
import sys, os, subprocess

text = sys.argv[1]
out = sys.argv[2]
voice = sys.argv[3] if len(sys.argv) > 3 else None
here = os.path.dirname(os.path.abspath(__file__))

if os.environ.get("ARK_API_KEY"):
    # ===== 豆包后端(本地优先,中文好)=====
    spk = voice or "zh_female_gaolengyujie_uranus_bigtts"
    subprocess.run(
        [sys.executable, os.path.join(here, "doubao_tts.py"), text, out, spk],
        check=True,
    )
else:
    # ===== Kokoro 后端(开源默认,免费本地)=====
    vc = voice or "zf_xiaobei"
    wav_tmp = out + ".kokoro.wav"
    # hyperframes tts 首次会下载 voice data(~27MB,需能访问 GitHub)
    subprocess.run(
        ["npx", "-y", "hyperframes", "tts", text,
         "--voice", vc, "--lang", "zh", "--output", wav_tmp],
        check=True,
    )
    if out.lower().endswith(".mp3"):
        # kokoro 出 wav,统一转 mp3(composition 用法一致)
        subprocess.run(["ffmpeg", "-y", "-i", wav_tmp, out],
                       check=True, capture_output=True)
        os.remove(wav_tmp)
    print(f"OK (kokoro) {out} voice={vc}")
