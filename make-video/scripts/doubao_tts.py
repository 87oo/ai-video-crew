#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""豆包语音合成 doubao-seed-tts-2.0(HTTP 非流式)。
返回 JSON,需 base64 解码 data 字段才是 mp3。
用法: python doubao_tts.py <文本> <输出.mp3> [音色]
key 从环境变量 ARK_API_KEY 读(对应 X-Api-Key header)。
"""
import urllib.request, json, uuid, sys, os, base64

KEY = os.environ.get("ARK_API_KEY")
if not KEY:
    print("ERROR: 环境变量 ARK_API_KEY 未设置。先 setx ARK_API_KEY \"ark-...\" 再重开终端。")
    sys.exit(1)

text = sys.argv[1]
out = sys.argv[2]
speaker = sys.argv[3] if len(sys.argv) > 3 else "zh_female_gaolengyujie_uranus_bigtts"

body = json.dumps({"req_params": {
    "text": text,
    "speaker": speaker,
    "audio_params": {"format": "mp3", "sample_rate": 24000}
}}).encode()

req = urllib.request.Request(
    "https://openspeech.bytedance.com/api/v3/plan/tts/unidirectional",
    data=body,
    headers={
        "X-Api-Key": KEY,
        "X-Api-Resource-Id": "seed-tts-2.0",
        "X-Api-Connect-Id": str(uuid.uuid4()),
        "Content-Type": "application/json",
    },
)
resp = urllib.request.urlopen(req, timeout=60).read().decode("utf-8")
# 返回是 JSONL:每行一个 {"code":0,"data":"<base64分片>"},末行 {"code":20000000,"message":"OK"}
audio_b64 = ""
for line in resp.split("\n"):
    line = line.strip()
    if not line:
        continue
    obj = json.loads(line)
    if obj.get("code") == 0 and obj.get("data"):
        audio_b64 += obj["data"]
    elif obj.get("code") not in (0, 20000000):
        print("TTS error:", obj.get("message"), obj)
        sys.exit(1)
audio = base64.b64decode(audio_b64)
with open(out, "wb") as f:
    f.write(audio)
print(f"OK {out} ({len(audio)} bytes mp3, speaker={speaker})")
