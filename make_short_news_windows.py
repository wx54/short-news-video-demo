"""
离线最小可运行示例（Windows 兼容）
- 使用 Pillow 生成字幕图像（无需 ImageMagick）
- pyttsx3 做离线 TTS（SAPI5），moviepy 做合成
- 所有路径都基于 E:\github
运行：python E:\github\make_short_news_windows.py
输出：E:\github\out\short_news.mp4
"""

import os
import sys
import math
import numpy as np
from moviepy.editor import (
    VideoFileClip, ImageClip, AudioFileClip, ColorClip,
    concatenate_videoclips, CompositeVideoClip
)
from PIL import Image, ImageDraw, ImageFont
import pyttsx3
import nltk

BASE_DIR = r"E:\github"
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUT_DIR = os.path.join(BASE_DIR, "out")
NEWS_FILE = os.path.join(BASE_DIR, "news.txt")
BG_VIDEO = os.path.join(ASSETS_DIR, "background.mp4")
OUT_VIDEO = os.path.join(OUT_DIR, "short_news.mp4")
TTS_AUDIO = os.path.join(OUT_DIR, "tts.wav")

WIDTH, HEIGHT = 1080, 1920
TARGET_DURATION = 60  # 目标时长（秒）

os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(OUT_DIR, exist_ok=True)

# 下载 punkt（若不存在）
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download('punkt', quiet=True)
from nltk.tokenize import sent_tokenize

# 1) 读取新闻
if not os.path.exists(NEWS_FILE):
    print("找不到新闻文件:", NEWS_FILE)
    print("请把新闻文本保存为 E:\\github\\news.txt 然后重试。")
    sys.exit(1)

with open(NEWS_FILE, "r", encoding="utf-8") as f:
    text = f.read().strip()
sents = sent_tokenize(text)
if not sents:
    print("新闻文本为空或无法解析。")
    sys.exit(1)

# 简单抽取压缩成适配时长的脚本（按字符估算）
chars_per_second = 15
max_chars = TARGET_DURATION * chars_per_second
selected = []
total_chars = 0
for s in sents:
    if total_chars + len(s) <= max_chars:
        selected.append(s)
        total_chars += len(s)
    else:
        break
script = "。".join(selected) if selected else text[:max_chars]
print("生成稿字数：", len(script))

# 2) TTS（pyttsx3）
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1.0)
print("合成离线语音到：", TTS_AUDIO)
engine.save_to_file(script, TTS_AUDIO)
engine.runAndWait()

# 3) 背景准备
audio_clip = AudioFileClip(TTS_AUDIO)
audio_dur = audio_clip.duration
print("语音时长（秒）：", audio_dur)

bg_clip = None
if os.path.exists(BG_VIDEO):
    print("使用背景视频：", BG_VIDEO)
    bg = VideoFileClip(BG_VIDEO)
    # 缩放并中心裁切为 1080x1920
    bg = bg.resize(width=WIDTH)
    if bg.h < HEIGHT:
        bg = bg.resize(height=HEIGHT)
    bg = bg.crop(x_center=bg.w/2, y_center=bg.h/2, width=WIDTH, height=HEIGHT)
    if bg.duration < audio_dur:
        n = int(math.ceil(audio_dur / bg.duration))
        bg = concatenate_videoclips([bg] * n).subclip(0, audio_dur)
    else:
        bg = bg.subclip(0, audio_dur)
    bg_clip = bg
else:
    # 纯色背景占位
    bg_clip = ColorClip(size=(WIDTH, HEIGHT), color=(18,18,18)).set_duration(audio_dur)

# 4) 生成字幕图片（Pillow），把文本按每行字符分割并按时间段显示
def split_text_to_lines(text, max_chars=18):
    lines = []
    cur = ""
    for ch in text:
        cur += ch
        if len(cur) >= max_chars:
            lines.append(cur)
            cur = ""
    if cur:
        lines.append(cur)
    return lines

lines = split_text_to_lines(script, max_chars=18)
n = max(1, len(lines))
sub_duration = audio_dur / n


def make_text_image(line, width=int(WIDTH*0.9), fontsize=56, padding=20):
    # 创建 RGBA 图片，白字黑描边
    try:
        font = ImageFont.truetype("arial.ttf", fontsize)
    except:
        font = ImageFont.load_default()
    # 估算高度
    temp = Image.new("RGBA", (width, 2000), (255,255,255,0))
    draw = ImageDraw.Draw(temp)
    _, h = draw.textbbox((0,0), line, font=font)[2:]
    h_total = h + padding * 2
    img = Image.new("RGBA", (width, h_total), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    x = width // 2
    y = h_total // 2
    # 黑描边
    outline_range = 2
    for ox in range(-outline_range, outline_range + 1):
        for oy in range(-outline_range, outline_range + 1):
            draw.text((x + ox, y + oy), line, font=font, anchor="mm", fill=(0,0,0,200))
    draw.text((x, y), line, font=font, anchor="mm", fill=(255,255,255,255))
    return img

text_clips = []
for i, line in enumerate(lines):
    t0 = i * sub_duration
    duration = min(sub_duration, audio_dur - t0)
    img = make_text_image(line)
    arr = np.array(img)
    txt_clip = ImageClip(arr).set_start(t0).set_duration(duration).set_position(("center", int(HEIGHT*0.78)))
    text_clips.append(txt_clip)

# 5) 标题卡
title_text = "热点快报：" + (sents[0][:20] if sents else "新闻")
title_img = make_text_image(title_text, fontsize=80)
title_clip = ImageClip(np.array(title_img)).set_duration(2).set_position(("center", int(HEIGHT*0.12)))

# 6) 合成
final = CompositeVideoClip([bg_clip, title_clip] + text_clips)
final = final.set_audio(audio_clip)
final = final.set_duration(audio_dur)
final = final.set_fps(24)

print("开始导出到：", OUT_VIDEO)
final.write_videofile(OUT_VIDEO, codec="libx264", audio_codec="aac", threads=4, bitrate="3000k")
print("生成完成！输出文件：", OUT_VIDEO)
