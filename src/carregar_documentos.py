from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document


# Diretórios
BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTOS_DIR = BASE_DIR / "documentos"

PDF_PATH = DOCUMENTOS_DIR / "base_conhecimento_vittamov.pdf"


def carregar_pdf():
    """Carrega o PDF da base de conhecimento."""

    if not PDF_PATH.exists():
        raise FileNotFoundError(
            f"PDF não encontrado: {PDF_PATH}"
        )

    loader = PyPDFLoader(str(PDF_PATH))
    documentos = loader.load()

    return documentos


def carregar_markdown():
    """Carrega todos os arquivos Markdown da pasta documentos."""

    documentos = []

    arquivos_md = list(DOCUMENTOS_DIR.glob("*.md"))

    for arquivo in arquivos_md:
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


def main():
    print("=" * 60)
    print("VITTAMOV — CARREGAMENTO DA BASE DE CONHECIMENTO")
    print("=" * 60)

    # PDF
    documentos_pdf = carregar_pdf()

    print(f"\n📄 PDF: {PDF_PATH.name}")
    print(f"   Páginas carregadas: {len(documentos_pdf)}")

    # Markdown
    documentos_md = carregar_markdown()

    print(f"\n📝 Arquivos Markdown encontrados: {len(documentos_md)}")

    for documento in documentos_md:
        print(f"   - {documento.metadata['source']}")

    # Base completa
    documentos = documentos_pdf + documentos_md

    print("\n" + "-" * 60)
    print(f"TOTAL DE DOCUMENTOS CARREGADOS: {len(documentos)}")
    print("-" * 60)

    # Amostra
    if documentos:
        primeiro = documentos[0]

        print("\n🔎 AMOSTRA DO PRIMEIRO DOCUMENTO")
        print(f"Origem: {primeiro.metadata}")

        texto = primeiro.page_content.strip()

        print("\nConteúdo:")
        print(texto[:1000])

        if len(texto) > 1000:
            print("\n[...]")

    print("\n" + "=" * 60)
    print("✅ Carregamento concluído com sucesso!")
    print("=" * 60)


if __name__ == "__main__":
    main()