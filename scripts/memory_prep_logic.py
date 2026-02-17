import os
import time
from pinecone import Pinecone
import hashlib

# Pinecone Configuration
# NOT: API Key'i environment variable'dan veya doğrudan buraya girmemiz gerekebilir.
# Ancak MCP server zaten bağlı olduğu için bu scripti MCP üzerinden değil,
# doğrudan Python ile çalıştıracaksak API Key lazım.
# Kullanıcıdan API key istemek yerine, bu işlemi MCP tool'ları ile yapacağım.
# Bu script SADECE mantığı göstermek ve dosya içeriğini hazırlamak içindir.
# Asıl işlem "scripts/sync_memory_mcp.py" olarak revize edilecek ve benim tarafımdan
# 'mcp_pinecone-mcp-server_upsert-records' tool'u kullanılarak parça parça yapılacak.

print("Starting memory analysis...")


def get_file_content(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Skipping binary or unreadable file: {filepath}")
        return None


def chunk_text(text, chunk_size=3000):
    # Basit bir chunking: 3000 karakterlik parçalara böl
    # Daha akıllıca: Fonksiyon/sınıf bazlı bölme (ileriki aşama)
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


# Hedef dosyaları topla
target_extensions = [
    ".py",
    ".js",
    ".html",
    ".css",
    ".md",
    ".txt",
    ".bat",
    ".ps1",
    ".json",
]
exclude_dirs = ["node_modules", "venv", ".git", "__pycache__", ".idea", ".vscode"]
files_to_index = []

root_dir = "."

for root, dirs, files in os.walk(root_dir):
    # Exclude directories
    dirs[:] = [d for d in dirs if d not in exclude_dirs]

    for file in files:
        if any(file.endswith(ext) for ext in target_extensions):
            files_to_index.append(os.path.join(root, file))

print(f"Found {len(files_to_index)} files to process.")
