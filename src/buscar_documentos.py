from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "vittamov"


# ============================================================
# MODELO DE EMBEDDINGS
# ============================================================

print("Carregando modelo de embeddings local...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Modelo carregado.")


# ============================================================
# CONECTAR AO CHROMADB
# ============================================================

print("\nConectando ao ChromaDB...")

vectorstore = Chroma(
    collection_name=COLLECTION_NAME,
    persist_directory=str(CHROMA_DIR),
    embedding_function=embeddings,
)

print("ChromaDB conectado.")


# ============================================================
# BUSCA SEMÂNTICA
# ============================================================

pergunta = "A clínica oferece fisioterapia ortopédica?"

print(f"\nPergunta: {pergunta}")
print("\nBuscando documentos relevantes...\n")

resultados = vectorstore.similarity_search_with_score(
    pergunta,
    k=3
)


# ============================================================
# EXIBIR RESULTADOS
# ============================================================

for i, (documento, score) in enumerate(resultados, start=1):

    print("=" * 70)
    print(f"RESULTADO {i}")
    print(f"Score: {score:.4f}")
    print(f"Origem: {documento.metadata}")
    print("\nConteúdo:")
    print(documento.page_content[:1000])
    print()