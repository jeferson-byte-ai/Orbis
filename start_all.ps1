# Script para iniciar Backend e Frontend do Orbis
# Execute com: .\start_all.ps1

Write-Host "🚀 Iniciando Orbis - Sistema Completo" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Verifica se está na pasta correta
if (-not (Test-Path ".\backend")) {
    Write-Host "❌ ERRO: Execute este script na raiz do projeto (onde está a pasta backend)" -ForegroundColor Red
    Write-Host "Exemplo: cd C:\Users\Jeferson\Documents\orbis" -ForegroundColor Yellow
    Write-Host "         .\start_all.ps1" -ForegroundColor Yellow
    pause
    exit 1
}

# Verifica se Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERRO: Python não encontrado. Instale Python 3.8+ primeiro." -ForegroundColor Red
    Write-Host "Download: https://www.python.org/downloads/" -ForegroundColor Yellow
    pause
    exit 1
}

# Verifica se Node.js está instalado
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js encontrado: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERRO: Node.js não encontrado. Instale Node.js primeiro." -ForegroundColor Red
    Write-Host "Download: https://nodejs.org/" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""
Write-Host "📦 Verificando dependências..." -ForegroundColor Yellow

# Verifica se dependências Python estão instaladas
if (-not (Test-Path ".\venv")) {
    Write-Host "⚠️  Virtual environment não encontrado. Criando..." -ForegroundColor Yellow
    python -m venv venv
}

# Verifica se dependências Node estão instaladas
if (-not (Test-Path ".\frontend\node_modules")) {
    Write-Host "⚠️  Dependências Node não encontradas. Instalando..." -ForegroundColor Yellow
    Set-Location frontend
    npm install
    Set-Location ..
}

Write-Host ""
Write-Host "🔥 Iniciando serviços..." -ForegroundColor Cyan
Write-Host ""

# Inicia Backend em nova janela
Write-Host "📡 Iniciando Backend na porta 8000..." -ForegroundColor Green
$backendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; python start.py" -PassThru

# Aguarda 5 segundos para o backend iniciar
Write-Host "⏳ Aguardando backend inicializar (5 segundos)..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# Testa se backend está respondendo
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Backend iniciado com sucesso!" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend pode não ter iniciado corretamente. Verifique a janela do backend." -ForegroundColor Yellow
}

Write-Host ""

# Inicia Frontend em nova janela
Write-Host "🌐 Iniciando Frontend na porta 3000..." -ForegroundColor Green
Set-Location frontend
$frontendJob = Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; npm run dev" -PassThru
Set-Location ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ ORBIS INICIADO COM SUCESSO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📍 URLs de Acesso:" -ForegroundColor Yellow
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🛑 Para PARAR os serviços:" -ForegroundColor Yellow
Write-Host "   - Feche as janelas do Backend e Frontend" -ForegroundColor White
Write-Host "   - Ou pressione Ctrl+C em cada janela" -ForegroundColor White
Write-Host ""
Write-Host "💡 Dica: Mantenha esta janela aberta para ver o status" -ForegroundColor Cyan
Write-Host ""

# Aguarda user input para não fechar
Write-Host "Pressione qualquer tecla para abrir o navegador..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Abre o navegador
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "✅ Navegador aberto! Aguardando serviços rodarem..." -ForegroundColor Green
Write-Host ""
Write-Host "Para fechar tudo, pressione Ctrl+C aqui e feche as outras janelas." -ForegroundColor Yellow

# Mantém o script rodando
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Write-Host ""
    Write-Host "🛑 Encerrando serviços..." -ForegroundColor Yellow
}
