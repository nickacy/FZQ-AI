<#
FZQ-AI Frontend V23 Audit Clean Script
审计基准：《CN 大模型审计工作书（V23）》
作用：扫描前端废弃备份、缓存、临时文件、遗留调试垃圾、旧规范兼容代码
#>
$rootPath = "C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI"
$frontSrc = Join-Path $rootPath "src/frontend"
$reportTime = Get-Date -Format "yyyyMMdd_HHmmss"
$reportFile = Join-Path $rootPath "frontend_clean_report_$reportTime.txt"

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "FZQ-AI 前端垃圾文件审计扫描启动" -ForegroundColor Cyan
Write-Host "项目根目录: $rootPath"
Write-Host "审计报告输出: $reportFile"
Write-Host "=====================================`n" -ForegroundColor Cyan

# 初始化报告
"# FZQ-AI 前端清理审计报告 $reportTime" | Out-File $reportFile
"审计范围: $frontSrc`n" | Out-File $reportFile -Append

# ======================
# 1. 定义待清理黑名单规则
# ======================
# 缓存/打包临时目录
$cacheDirPattern = @(
    ".vite", ".cache", ".parcel-cache",
    "dist_bak", "dist_old", "dist_v*",
    "dashboard_backup", "build_temp", "tmp_build"
)
# 备份/临时草稿文件后缀
$bakFilePattern = @("*_bak.*", "*_old.*", "*_temp.*", "*_draft.*", "*_copy.*")
# 调试日志、脏测试JSON
$debugFilePattern = @("*.log", "tmp_*.json", "*broken_format*.json", "local_debug.json")
# 废弃单页调试HTML
$debugHtmlPattern = @("test_*.html", "temp_*.html", "debug_*.html")

# ======================
# 2. 扫描缓存目录
# ======================
Write-Host "[1/4] 扫描构建缓存与历史打包目录" -ForegroundColor Yellow
$delDirList = @()
foreach ($pat in $cacheDirPattern) {
    $findDirs = Get-ChildItem -Path $frontSrc -Recurse -Directory -Filter $pat -ErrorAction SilentlyContinue
    if ($findDirs.Count -gt 0) {
        $delDirList += $findDirs.FullName
    }
}
if ($delDirList.Count -gt 0) {
    "## 待删除缓存/打包目录（$($delDirList.Count) 个）`n" | Out-File $reportFile -Append
    $delDirList | ForEach-Object { "- $_" | Out-File $reportFile -Append }
}
else {
    "## 待删除缓存/打包目录：无`n" | Out-File $reportFile -Append
}

# ======================
# 3. 扫描备份、临时、调试文件
# ======================
Write-Host "[2/4] 扫描备份/草稿/临时测试文件" -ForegroundColor Yellow
$delFileList = @()
$allFilePatterns = $bakFilePattern + $debugFilePattern + $debugHtmlPattern
foreach ($pat in $allFilePatterns) {
    $findFiles = Get-ChildItem -Path $frontSrc -Recurse -File -Filter $pat -ErrorAction SilentlyContinue
    if ($findFiles.Count -gt 0) {
        $delFileList += $findFiles.FullName
    }
}
if ($delFileList.Count -gt 0) {
    "## 待删除临时/备份文件（$($delFileList.Count) 个）`n" | Out-File $reportFile -Append
    $delFileList | ForEach-Object { "- $_" | Out-File $reportFile -Append }
}
else {
    "## 待删除临时/备份文件：无`n" | Out-File $reportFile -Append
}

# ======================
# 4. 代码内审计：检索废弃硬编码、调试垃圾（仅输出检索，不删文件）
# ======================
Write-Host "[3/4] 扫描源码内违规废弃代码标记（仅审计，不删除文件）" -ForegroundColor Yellow
$codeScanList = @()
# V23 不兼容旧规范关键词
$scanKeywords = @(
    "indent: 4",                # 旧4空格缩进硬编码
    "signals(?!policy|trend)",  # 未拆分原生signals
    "actors.*facts.*events",    # 旧错误字段渲染顺序
    "debugger",
    "console.log.*MiniMax",
    "console.log.*原始报文"
)
"## 源码内待清理代码片段检索清单`n" | Out-File $reportFile -Append
foreach ($kw in $scanKeywords) {
    $matchFiles = Get-ChildItem -Path $frontSrc -Recurse -Include *.js,*.ts,*.vue,*.html,*.css -ErrorAction SilentlyContinue `
        | Select-String -Pattern $kw -ErrorAction SilentlyContinue | Select-Object -Unique Path
    if ($matchFiles) {
        "关键词匹配：$kw" | Out-File $reportFile -Append
        $matchFiles.Path | ForEach-Object { "  - $_" | Out-File $reportFile -Append }
        $codeScanList += $matchFiles.Path
    }
}
if ($codeScanList.Count -eq 0) {
    "无匹配废弃硬编码/调试代码" | Out-File $reportFile -Append
}

# ======================
# 5. 输出统计汇总
# ======================
Write-Host "`n=====================================" -ForegroundColor Green
Write-Host "扫描完成！统计汇总" -ForegroundColor Green
Write-Host "缓存打包目录待清理：$($delDirList.Count) 个"
Write-Host "临时备份文件待清理：$($delFileList.Count) 个"
Write-Host "存在废弃代码的源码文件：$($codeScanList.Count) 个"
Write-Host "审计报告路径：$reportFile"
Write-Host "=====================================`n" -ForegroundColor Green

# ======================
# 6. 交互式确认删除（安全二次校验）
# ======================
if (($delDirList.Count -gt 0) -or ($delFileList.Count -gt 0)) {
    $confirm = Read-Host "确认执行删除操作？输入 Y 执行删除，其他任意字符仅退出不删除"
    if ($confirm -eq "Y" -or $confirm -eq "y") {
        Write-Host "开始删除目录..." -ForegroundColor Red
        $delDirList | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "开始删除临时文件..." -ForegroundColor Red
        $delFileList | Remove-Item -Force -ErrorAction SilentlyContinue
        Write-Host "删除完成！请查看审计报告核对已清理内容" -ForegroundColor Green
    }
    else {
        Write-Host "已取消删除，仅生成审计报告，无文件改动" -ForegroundColor Yellow
    }
}
else {
    Write-Host "未扫描到可清理垃圾文件，无需执行删除" -ForegroundColor Green
}