# ============================================================
# VITTAMOV — SISTEMA RAG
# Recuperação de documentos + Gemini
# ============================================================

from pathlib import Path
import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CHROMA_DIR = BASE_DIR / "chroma_db"

COLLECTION_NAME = "vittamov"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Modelo que já foi testado e funcionou com sua API Key
GEMINI_MODEL = "gemini-3.5-flash"

TOP_K = 4


# ============================================================
# VARIÁVEIS DE AMBIENTE
# ============================================================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY não encontrada. "
        "Verifique o arquivo .env."
    )


# ============================================================
# CARREGAR EMBEDDINGS
# ============================================================

def carregar_embeddings():

    print("Carregando modelo de embeddings local...")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    print("Modelo de embeddings carregado.")

    return embeddings


# ============================================================
# CONECTAR AO CHROMADB
# ============================================================

def carregar_banco_vetorial(embeddings):

    print("Conectando ao ChromaDB...")

    if not CHROMA_DIR.exists():
        raise FileNotFoundError(
            f"Banco vetorial não encontrado em:\n{CHROMA_DIR}"
        )

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
    )

    quantidade = vectorstore._collection.count()

    print(f"ChromaDB conectado. Documentos: {quantidade}")

    if quantidade == 0:
        raise ValueError(
            "A coleção vittamov está vazia."
        )

    return vectorstore


# ============================================================
# CARREGAR MODELO GEMINI
# ============================================================

def carregar_modelo():

    print("Conectando ao Gemini...")

    model = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=GOOGLE_API_KEY,
        temperature=0.2,
        max_retries=0,
    )

    print(f"Gemini conectado: {GEMINI_MODEL}")

    return model


# ============================================================
# BUSCAR DOCUMENTOS
# ============================================================

def buscar_documentos(vectorstore, pergunta):

    print("\nBuscando informações relevantes...")

    resultados = vectorstore.similarity_search_with_score(
        pergunta,
        k=TOP_K
    )

    if not resultados:
        return []

    documentos = []

    for documento, score in resultados:

        documentos.append({
            "documento": documento,
            "score": score,
        })

    return documentos


# ============================================================
# MONTAR CONTEXTO
# ============================================================

def montar_contexto(resultados):

    partes = []

    for i, resultado in enumerate(resultados, start=1):

        documento = resultado["documento"]
        score = resultado["score"]

        fonte = documento.metadata.get(
            "source",
            "Fonte não informada"
        )

        conteudo = documento.page_content

        partes.append(
            f"""
DOCUMENTO {i}
Fonte: {fonte}
Distância semântica: {score:.4f}

Conteúdo:
{conteudo}
"""
        )

    return "\n".join(partes)


# ============================================================
# EXTRAIR TEXTO DA RESPOSTA DO GEMINI
# ============================================================

def extrair_texto(resposta):

    conteudo = resposta.content

    # Normalmente o Gemini retorna string
    if isinstance(conteudo, str):
        return conteudo.strip()

    # Algumas versões retornam uma lista de blocos
    if isinstance(conteudo, list):

        textos = []

        for bloco in conteudo:

            if isinstance(bloco, str):
                textos.append(bloco)

            elif isinstance(bloco, dict):

                texto = bloco.get("text")

                if texto:
                    textos.append(texto)

        return "\n".join(textos).strip()

    return str(conteudo).strip()


# ============================================================
# GERAR RESPOSTA
# ============================================================

def gerar_resposta(model, pergunta, contexto):

    prompt = f"""
Você é o assistente virtual da Clínica VittaMov.

Sua função é responder perguntas utilizando EXCLUSIVAMENTE
as informações presentes no contexto fornecido.

REGRAS IMPORTANTES:

1. Não invente informações.
2. Não utilize conhecimento externo ao contexto.
3. Se a informação não estiver no contexto, diga claramente
   que não encontrou essa informação na base de conhecimento.
4. Responda em português do Brasil.
5. Seja objetivo, claro e cordial.
6. Não faça diagnóstico médico.
7. Não prescreva tratamentos ou medicamentos.
8. Quando apropriado, recomende avaliação de um profissional.

CONTEXTO DA BASE DE CONHECIMENTO:

{contexto}

PERGUNTA DO USUÁRIO:

{pergunta}

Responda somente à pergunta do usuário.
"""

    try:

        resposta = model.invoke(prompt)

        return extrair_texto(resposta)

    except Exception as erro:

        print("\nERRO REAL DO GEMINI:")
        print(erro)

        mensagem = str(erro)

        if "429" in mensagem or "RESOURCE_EXHAUSTED" in mensagem:

            return (
                "O serviço de geração atingiu temporariamente "
                "o limite de utilização da API do Gemini. "
                "A busca na base de conhecimento foi realizada, "
                "mas a resposta automática não pôde ser gerada."
            )

        if "404" in mensagem or "NOT_FOUND" in mensagem:

            return (
                "O modelo configurado para geração não está "
                "disponível para esta API Key."
            )

        return (
            "Não foi possível gerar a resposta neste momento."
        )


# ============================================================
# RESPONDER PERGUNTA
# ============================================================

def responder(pergunta, vectorstore, model):

    resultados = buscar_documentos(
        vectorstore,
        pergunta
    )

    if not resultados:

        return (
            "Não encontrei informações relevantes "
            "na base de conhecimento da Clínica VittaMov."
        )

    contexto = montar_contexto(resultados)

    print(
        f"Documentos recuperados: {len(resultados)}"
    )

    print("\nGerando resposta com Gemini...")

    resposta = gerar_resposta(
        model,
        pergunta,
        contexto
    )

    return resposta


# ============================================================
# EXIBIR FONTES
# ============================================================

def exibir_fontes(resultados):

    fontes = []

    for resultado in resultados:

        fonte = resultado["documento"].metadata.get(
            "source"
        )

        if fonte and fonte not in fontes:
            fontes.append(fonte)

    if not fontes:
        return

    print("\n" + "=" * 60)
    print("FONTES CONSULTADAS")
    print("=" * 60)

    for fonte in fontes:
        print(f"- {fonte}")


# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():

    print("=" * 60)
    print("VITTAMOV — SISTEMA RAG")
    print("=" * 60)

    try:

        embeddings = carregar_embeddings()

        vectorstore = carregar_banco_vetorial(
            embeddings
        )

        model = carregar_modelo()

    except Exception as erro:

        print("\nERRO NA INICIALIZAÇÃO")
        print("=" * 60)
        print(erro)
        return

    print("\nSistema pronto!")
    print("Digite 'sair' para encerrar.")

    while True:

        print("\n" + "-" * 60)

        pergunta = input("Pergunta: ").strip()

        if not pergunta:
            continue

        if pergunta.lower() in {
            "sair",
            "exit",
            "quit"
        }:
            print("\nEncerrando sistema RAG...")
            break

        resultados = buscar_documentos(
            vectorstore,
            pergunta
        )

        if not resultados:

            print("\n" + "=" * 60)
            print("RESPOSTA")
            print("=" * 60)

            print(
                "Não encontrei informações relevantes "
                "na base de conhecimento da Clínica VittaMov."
            )

            continue

        print(
            f"\nDocumentos recuperados: {len(resultados)}"
        )

        print("\nGerando resposta com Gemini...")

        contexto = montar_contexto(resultados)

        resposta = gerar_resposta(
            model,
            pergunta,
            contexto
        )

        print("\n" + "=" * 60)
        print("RESPOSTA")
        print("=" * 60)
        print(resposta)

        exibir_fontes(resultados)

    print("\n" + "=" * 60)
    print("RAG FINALIZADO")
    print("=" * 60)


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":
    main()