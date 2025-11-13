# 🚀 Como Rodar o Orbis Localmente

## ⚡ Quick Start (5 minutos)

### 1. **Ative o ambiente virtual**
```powershell
cd C:\Users\Jeferson\Documents\orbis
.\venv\Scripts\activate
```

### 2. **Inicie o Backend**
```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

**Aguarde:** O servidor vai carregar os modelos de ML (pode demorar 1-2 minutos na primeira vez)

**Pronto!** Quando ver:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 3. **Inicie o Frontend** (em outro terminal)
```powershell
cd C:\Users\Jeferson\Documents\orbis\frontend
npm run dev
```

### 4. **Acesse:**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 🔧 Resolução de Problemas

### ❌ Erro: "ValidationError: Field required"
**Solução:** Faltou o arquivo `.env`

✅ **JÁ ESTÁ RESOLVIDO!** O arquivo `.env` já foi criado automaticamente.

Caso precise recriar:
```powershell
Copy-Item archives\.env .env
```

### ❌ Erro: "Module not found"
**Solução:** Instale as dependências
```powershell
.\venv\Scripts\activate
pip install -r requirements.txt
```

### ❌ Erro: "Port 8000 already in use"
**Solução:** Mate o processo na porta 8000
```powershell
# Encontre o processo
netstat -ano | findstr :8000

# Mate o processo (substitua PID pelo número encontrado)
taskkill /PID <PID> /F
```

Ou use outra porta:
```powershell
uvicorn backend.main:app --host 0.0.0.0 --port 8001 --reload
```

### ❌ Frontend não conecta ao backend
**Solução:** Verifique se o backend está rodando

1. Abra http://localhost:8000/health
2. Se funcionar, backend está OK
3. Se não, reinicie o backend

---

## 📝 Comandos Úteis

### Testar se tudo está OK:
```powershell
# Testar imports
python -c "from backend.main import app; print('✅ Backend OK')"

# Testar config
python -c "from backend.config import settings; print('✅ Config OK')"

# Verificar banco de dados
ls data\orbis.db
```

### Limpar e reiniciar:
```powershell
# Parar todos os servidores (Ctrl+C)

# Limpar cache
rm -r backend\__pycache__ -Force -ErrorAction SilentlyContinue
rm -r backend\*\__pycache__ -Force -ErrorAction SilentlyContinue

# Reiniciar backend
uvicorn backend.main:app --reload
```

### Ver logs em tempo real:
```powershell
# Logs do backend aparecem no terminal onde você rodou uvicorn
# Para ver logs salvos:
cat logs\*.log | Select-Object -Last 50
```

---

## 🎯 Próximos Passos

### Para Desenvolvimento:
1. **Edite o código** - Uvicorn tem hot-reload ativado
2. **Teste mudanças** em http://localhost:8000/docs
3. **Veja logs** no terminal

### Para Produção:
1. Leia `docs/deployment/` para guias de deploy
2. Configure PostgreSQL (ao invés de SQLite)
3. Configure Redis para cache
4. Use Docker: `docker-compose up`

---

## 📚 Mais Informações

- **Documentação Completa**: `docs/README.md`
- **API Docs**: http://localhost:8000/docs (quando rodando)
- **Arquitetura**: `docs/architecture/`
- **Deploy**: `docs/deployment/`
- **Troubleshooting**: `docs/fixes/`

---

## ✅ Checklist de Primeiro Uso

- [x] ✅ Ambiente virtual criado
- [x] ✅ Dependências instaladas
- [x] ✅ Arquivo .env configurado
- [ ] Backend rodando (faça agora!)
- [ ] Frontend rodando
- [ ] Testou http://localhost:8000/docs
- [ ] Criou sua primeira conta
- [ ] Testou voice cloning

---

## 💡 Dicas

### Performance:
- Primeira inicialização é lenta (carregando modelos ML)
- Depois fica rápido (<2s para iniciar)
- Use `ML_LAZY_LOAD=true` no .env para carregar modelos sob demanda

### Desenvolvimento:
- Use `DEBUG=true` no .env para ver mais logs
- API Docs interativo em /docs é seu melhor amigo
- Frontend hot-reload está ativo

### Produção:
- **NUNCA** use as secrets do .env atual em produção
- Gere novas secrets: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- Use PostgreSQL ao invés de SQLite
- Configure HTTPS/SSL

---

## 🆘 Precisa de Ajuda?

1. **Leia a documentação** em `docs/`
2. **Verifique logs** no terminal
3. **Teste o health check**: http://localhost:8000/health
4. **Revise o .env** para ver se está tudo configurado

---

<div align="center">

**Pronto para começar!** 🚀

Execute: `uvicorn backend.main:app --reload`

</div>
