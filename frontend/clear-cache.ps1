Write-Host "🧹 Limpando cache do projeto..." -ForegroundColor Cyan

# Limpar cache do Vite
if (Test-Path "node_modules/.vite") {
    Remove-Item -Recurse -Force "node_modules/.vite"
    Write-Host "✓ Cache do Vite limpo" -ForegroundColor Green
}

# Limpar dist
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "✓ Pasta dist limpa" -ForegroundColor Green
}

Write-Host "`n✅ Cache limpo com sucesso!" -ForegroundColor Green
Write-Host "Agora execute: npm run dev" -ForegroundColor Yellow
