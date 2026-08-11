from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTOS_DIR = BASE_DIR / "documentos"
PDF_PATH = DOCUMENTOS_DIR / "base_conhecimento_vittamov.pdf"


def carregar_pdf():
    """Carrega o PDF da base de conhecimento."""

    loader = PyPDFLoader(str(PDF_PATH))
    return loader.load()


def carregar_markdown():
    """Carrega os arquivos Markdown."""

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
    """Carrega toda a base documental."""

    documentos_pdf = carregar_pdf()
    documentos_md = carregar_markdown()

    return documentos_pdf + documentos_md


def dividir_documentos(documentos):
    """Divide os documentos em chunks."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    return splitter.split_documents(documentos)


def main():
    print("=" * 60)
    print("VITTAMOV — DIVISÃO DA BASE DE CONHECIMENTO")
    print("=" * 60)

    documentos = carregar_documentos()

    print(f"\n📚 Documentos originais: {len(documentos)}")

    chunks = dividir_documentos(documentos)

    print(f"🧩 Chunks gerados: {len(chunks)}")

    print("\n" + "-" * 60)
    print("AMOSTRAS DOS CHUNKS")
    print("-" * 60)

    for i, chunk in enumerate(chunks[:5], start=1):
        print(f"\n### CHUNK {i}")
        print(f"Origem: {chunk.metadata}")
        print(f"Tamanho: {len(chunk.page_content)} caracteres")
        print("\nConteúdo:")
        print(chunk.page_content[:500])

    print("\n" + "=" * 60)
    print("✅ Divisão concluída com sucesso!")
    print("=" * 60)


if __name__ == "__main__":
    main()