"""
Quick server test script
"""
import sys
import time
import subprocess
import requests
from pathlib import Path

def test_server():
    print("🧪 Testando servidor Orbis...\n")
    
    # Start server
    print("🚀 Iniciando servidor...")
    venv_python = Path("venv/Scripts/python.exe")
    
    if not venv_python.exists():
        print("❌ venv não encontrado!")
        return False
    
    process = subprocess.Popen(
        [str(venv_python), "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    print("⏳ Aguardando servidor iniciar...")
    time.sleep(10)
    
    try:
        # Test endpoints
        tests = [
            ("Health Check", "http://localhost:8000/health"),
            ("API Docs", "http://localhost:8000/docs"),
            ("Root", "http://localhost:8000/"),
        ]
        
        results = []
        for name, url in tests:
            try:
                response = requests.get(url, timeout=5)
                status = "✅" if response.status_code < 400 else "⚠️"
                results.append(f"{status} {name}: {response.status_code}")
            except Exception as e:
                results.append(f"❌ {name}: {str(e)}")
        
        print("\n📊 Resultados dos testes:")
        for result in results:
            print(f"  {result}")
        
        print("\n✅ Servidor rodando em: http://localhost:8000")
        print("📚 Documentação em: http://localhost:8000/docs")
        print("\n⚠️  Pressione Ctrl+C para parar o servidor")
        
        # Keep running
        process.wait()
        
    except KeyboardInterrupt:
        print("\n\n🛑 Parando servidor...")
        process.terminate()
        process.wait()
        print("✅ Servidor parado!")
        return True
    except Exception as e:
        print(f"\n❌ Erro no teste: {e}")
        process.terminate()
        return False

if __name__ == "__main__":
    test_server()
