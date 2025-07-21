#!/usr/bin/env python3
"""
Script para executar a aplicação Financial Management API
"""

import sys
import os
import subprocess
from pathlib import Path

# Adicionar o diretório atual ao Python path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

def install_dependencies():
    """Instala as dependências do projeto"""
    print("📦 Instalando dependências...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def run_development():
    """Executa a aplicação em modo desenvolvimento"""
    print("🚀 Iniciando servidor de desenvolvimento...")
    
    # Definir variáveis de ambiente
    os.environ.setdefault("PYTHONPATH", str(ROOT_DIR))
    
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["app"],
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn não encontrado. Instalando dependências...")
        install_dependencies()
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            reload_dirs=["app"],
            log_level="info"
        )

def main():
    """Função principal"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "install":
            install_dependencies()
        elif command == "dev":
            run_development()
        elif command == "help":
            print("""
Comandos disponíveis:
  install  - Instala as dependências
  dev      - Executa em modo desenvolvimento
  help     - Mostra esta ajuda
            """)
        else:
            print(f"❌ Comando '{command}' não reconhecido. Use 'help' para ver os comandos disponíveis.")
    else:
        run_development()

if __name__ == "__main__":
    main()