from pathlib import Path
import chromadb

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"

print("=" * 60)
print("DIAGNÓSTICO DO CHROMADB")
print("=" * 60)

print(f"\nDiretório: {CHROMA_DIR}")
print(f"Existe: {CHROMA_DIR.exists()}")

client = chromadb.PersistentClient(
    path=str(CHROMA_DIR)
)

collections = client.list_collections()

print(f"\nColeções encontradas: {len(collections)}")
print("=" * 60)

for collection in collections:
    print(f"\nNome da coleção: {collection.name}")

    try:
        print(f"Quantidade de documentos: {collection.count()}")
    except Exception as e:
        print(f"Erro ao contar documentos: {e}")

print("\n" + "=" * 60)