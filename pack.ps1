# 自动打包 FZQ-AI 项目为 ZIP
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$zipPath = Join-Path $projectPath "FZQ-AI.zip"

Write-Host "正在打包项目到 $zipPath ..."

if (Test-Path $zipPath) {
    Remove-Item $zipPath -Force
}

Compress-Archive -Path "$projectPath\*" -DestinationPath $zipPath -Force

Write-Host "打包完成！ZIP 文件已生成：$zipPath"
