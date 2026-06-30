Write-Host "=== FZQ-AI V17 Cleanup Script ===" -ForegroundColor Cyan

# Set base path (your real project path)
$base = "C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI\src\fzq_ai"

# Helper function
function SafeDelete($path) {
    if (Test-Path $path) {
        Remove-Item $path -Force -Recurse
        Write-Host "Deleted: $path" -ForegroundColor Green
    } else {
        Write-Host "Not found (skipped): $path" -ForegroundColor DarkYellow
    }
}

Write-Host "`n--- Deleting old V17 entry layer files ---"
SafeDelete "$base\core\entry_layer_v17.py"
SafeDelete "$base\core\route_result.py"
SafeDelete "$base\core\routing_dev.py"

Write-Host "`n--- Deleting old V17 pipelines ---"
SafeDelete "$base\pipelines\v17_*"
SafeDelete "$base\pipelines\old_*"

Write-Host "`n--- Deleting old V17 test files ---"
SafeDelete "C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI\tests\test_entry_layer_v17.py"
SafeDelete "C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI\tests\test_pipeline_v17.py"
SafeDelete "C:\Users\nicka\FZQ-AI-WORKSPACE\FZQ-AI\tests\test_routing_v17.py"

Write-Host "`n--- Deleting old V17 LLM client ---"
SafeDelete "$base\llm\llm_client.py"

Write-Host "`n--- Deleting old V17 model router ---"
SafeDelete "$base\core\model_router_v17.py"

Write-Host "`n=== Cleanup Complete ===" -ForegroundColor Cyan
Write-Host "Your FZQ-AI project is now clean and ready for V21 tomorrow!" -ForegroundColor Magenta
