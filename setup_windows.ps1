# PowerShell 脚本：在 E:\github 下创建 assets 和 out，并下载一个示例背景视频供测试
# 运行方法（PowerShell）： .\setup_windows.ps1
$Base = "E:\github"
$Assets = Join-Path $Base "assets"
$Out = Join-Path $Base "out"
New-Item -ItemType Directory -Path $Assets -Force | Out-Null
New-Item -ItemType Directory -Path $Out -Force | Out-Null

Write-Host "Downloading sample background video to $Assets\background.mp4 ..."
# 小体积示例视频（用于演示）：如果被墙或不可用，请替换 URL
$sampleUrl = "https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4"
$dest = Join-Path $Assets "background.mp4"
try {
    Invoke-WebRequest -Uri $sampleUrl -OutFile $dest -UseBasicParsing -ErrorAction Stop
    Write-Host "下载完成：" $dest
} catch {
    Write-Warning "示例视频下载失败：$_"
    Write-Host "你可以手动把一个 mp4 放到 $Assets\background.mp4"
}

Write-Host "准备完成。若还未安装 Python 依赖，请在 PowerShell 中运行:"
Write-Host "pip install -r E:\github\requirements.txt"
Write-Host "然后运行: python E:\github\make_short_news_windows.py"
