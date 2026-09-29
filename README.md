# short-news-video-demo

离线示例：把一条新闻文本合成为 9:16 的短视频（Windows）。

目录结构：
- make_short_news_windows.py   # 主脚本，生成视频（不依赖 ImageMagick，使用 Pillow）
- setup_windows.ps1            # 可选：PowerShell 一键准备（下载示例素材）
- requirements.txt             # Python 依赖
- news.txt                     # 示例新闻文本（可替换）
- assets/                      # 背景素材（可由 setup_windows.ps1 下载）
- out/                         # 输出目录，最终 short_news.mp4 在此

快速步骤（建议）：
1. 在 Windows 上确保已安装 Python 3.8+（若未安装，请先安装）。
2. 将本仓库内容放到 E:\github。
3. 打开 PowerShell（可用管理员权限），运行：
   cd E:\github
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   .\setup_windows.ps1   # 可选：下载示例素材
   python .\make_short_news_windows.py

输出：E:\github\out\short_news.mp4

如果你希望我把脚本改为使用更高质量的本地 TTS（Coqui TTS），或把每条新闻生成多个 1 分钟片段以合并为一个 3–5 分钟成片，我可以继续修改脚本并给出一键脚本。
