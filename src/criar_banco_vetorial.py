from pathlib import Path

from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DOCUMENTOS_DIR = BASE_DIR / "documentos"
PDF_PATH = DOCUMENTOS_DIR / "base_conhecimento_vittamov.pdf"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "vittamov"


def carregar_pdf():
    loader = PyPDFLoader(str(PDF_PATH))
    return loader.load()


def carregar_markdown():
    documentos = []

    for arquivo in DOCUMENTOS_DIR.glob("*.md"):
        conteudo = arquivo.read_text(encoding="utf-8")

        documentos.append(
            Document(
                page_content=conteudo,
                metadata={
                    "source": arquivo.name,
                    "tipo": "markdown",
                },
            )
        )

    return documentos


def carregar_documentos():
    return carregar_pdf() + carregar_markdown()


def dividir_documentos(documentos):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    return splitter.split_documents(documentos)


def criar_embeddings():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


def criar_banco_vetorial(chunks):
    embeddings = criar_embeddings()

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_DIR),
    )

    vectorstore.add_documents(chunks)

    return vectorstore


def main():
    print("=" * 60)
    print("VITTAMOV - CRIACAO DO BANCO VETORIAL")
    print("=" * 60)

    print("\nCarregando documentos...")

    documentos = carregar_documentos()

    print(f"Documentos carregados: {len(documentos)}")

    print("\nDividindo documentos em chunks...")

    chunks = dividir_documentos(documentos)

    print(f"Chunks gerados: {len(chunks)}")

    print("\nCarregando modelo de embeddings local...")

    criar_embeddings()

    print("Modelo carregado.")

    print("\nArmazenando embeddings no ChromaDB...")

    criar_banco_vetorial(chunks)

    print("\n" + "-" * 60)
    print("BANCO VETORIAL CRIADO COM SUCESSO!")
    print("-" * 60)

    print(f"Colecao: {COLLECTION_NAME}")
    print(f"Chunks armazenados: {len(chunks)}")
    print("Dimensao dos embeddings: 384")
    print(f"Diretorio: {CHROMA_DIR}")

    print("\n" + "=" * 60)
    print("INDEXACAO CONCLUIDA!")
    print("=" * 60)


if __name__ == "__main__":
    main()
