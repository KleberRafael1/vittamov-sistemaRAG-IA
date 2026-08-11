# ============================================================
# VITTAMOV — API REST
# FastAPI + Sistema RAG
# ============================================================

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.rag import (
    carregar_embeddings,
    carregar_banco_vetorial,
    carregar_modelo,
    responder,
    buscar_documentos,
)


# ============================================================
# VARIÁVEIS GLOBAIS
# ============================================================

vectorstore = None
model = None


# ============================================================
# INICIALIZAÇÃO DO SISTEMA
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    global vectorstore
    global model

    print("=" * 60)
    print("VITTAMOV — INICIALIZANDO API")
    print("=" * 60)

    try:

        print("\nCarregando embeddings...")

        embeddings = carregar_embeddings()

        print("\nCarregando ChromaDB...")

        vectorstore = carregar_banco_vetorial(
            embeddings
        )

        print("\nCarregando Gemini...")

        model = carregar_modelo()

        print("\n" + "=" * 60)
        print("VITTAMOV — API PRONTA")
        print("=" * 60)

    except Exception as erro:

        print("\nERRO NA INICIALIZAÇÃO")
        print("=" * 60)
        print(erro)

        raise

    yield

    print("\n" + "=" * 60)
    print("VITTAMOV — API ENCERRADA")
    print("=" * 60)


# ============================================================
# CRIAÇÃO DA API
# ============================================================

app = FastAPI(
    title="VittaMov — Sistema RAG",
    description=(
        "API REST para consulta à base de conhecimento "
        "da Clínica VittaMov utilizando RAG e Google Gemini."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODELOS DE DADOS
# ============================================================

class PerguntaRequest(BaseModel):

    pergunta: str


class PerguntaResponse(BaseModel):

    resposta: str
    fontes: list[str]


# ============================================================
# ROTA PRINCIPAL
# ============================================================

@app.get("/")
def inicio():

    return {
        "sistema": "VittaMov",
        "descricao": "Sistema RAG com FastAPI + Gemini",
        "status": "online",
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "rag": vectorstore is not None,
        "gemini": model is not None,
    }


# ============================================================
# CONSULTA AO RAG
# ============================================================

@app.post(
    "/perguntar",
    response_model=PerguntaResponse
)
def perguntar(dados: PerguntaRequest):

    if vectorstore is None or model is None:

        raise HTTPException(
            status_code=503,
            detail="Sistema RAG ainda não foi inicializado.",
        )

    pergunta = dados.pergunta.strip()

    if not pergunta:

        raise HTTPException(
            status_code=400,
            detail="A pergunta não pode estar vazia.",
        )

    try:

        # ----------------------------------------------------
        # Busca dos documentos
        # ----------------------------------------------------

        resultados = buscar_documentos(
            vectorstore,
            pergunta
        )

        if not resultados:

            return PerguntaResponse(
                resposta=(
                    "Não encontrei informações relevantes "
                    "na base de conhecimento da Clínica VittaMov."
                ),
                fontes=[],
            )

        # ----------------------------------------------------
        # Geração da resposta
        # ----------------------------------------------------

        resposta = responder(
            pergunta,
            vectorstore,
            model
        )

        # ----------------------------------------------------
        # Recuperação das fontes
        # ----------------------------------------------------

        fontes = []

        for resultado in resultados:

            fonte = resultado["documento"].metadata.get(
                "source"
            )

            if fonte and fonte not in fontes:

                fontes.append(fonte)

        return PerguntaResponse(
            resposta=resposta,
            fontes=fontes,
        )

    except Exception as erro:

        print("\nERRO NA CONSULTA:")
        print(erro)

        raise HTTPException(
            status_code=500,
            detail=(
                "Não foi possível processar "
                "a pergunta neste momento."
            ),
        )