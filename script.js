
/* =========================================================
   VITTAMOV — ASSISTENTE VIRTUAL
   Integração com API FastAPI + RAG
   ========================================================= */

/* =========================================================
   CONFIGURAÇÃO DA API
   ========================================================= */

const API_BASE_URL = "http://127.0.0.1:8000";

const API_PERGUNTAR = `${API_BASE_URL}/perguntar`;
const API_HEALTH = `${API_BASE_URL}/health`;


/* =========================================================
   ELEMENTOS DA INTERFACE
   ========================================================= */

const chat = document.getElementById("chat");
const questionForm = document.getElementById("question-form");
const questionInput = document.getElementById("question");
const sendButton = document.getElementById("send-button");

const apiStatus = document.getElementById("api-status");
const statusText = apiStatus?.querySelector(".status-text");
const statusDot = apiStatus?.querySelector(".status-dot");

const suggestionButtons =
    document.querySelectorAll(".suggestion");


/* =========================================================
   STATUS DA API
   ========================================================= */

async function verificarAPI() {

    if (!apiStatus) {
        return;
    }

    try {

        const response = await fetch(API_HEALTH, {
            method: "GET"
        });

        if (!response.ok) {
            throw new Error("API indisponível");
        }

        const dados = await response.json();

        if (dados.status === "ok") {

            if (statusText) {
                statusText.textContent = "Assistente online";
            }

            if (statusDot) {
                statusDot.style.background = "#2fb344";
            }

        } else {

            throw new Error("API não está pronta");

        }

    } catch (erro) {

        console.warn(
            "Não foi possível verificar a API:",
            erro
        );

        if (statusText) {
            statusText.textContent = "Assistente offline";
        }

        if (statusDot) {
            statusDot.style.background = "#dc3545";
        }
    }
}


/* =========================================================
   ADICIONAR MENSAGEM DO USUÁRIO
   ========================================================= */

function adicionarMensagemUsuario(texto) {

    const mensagem = document.createElement("div");

    mensagem.classList.add(
        "message",
        "user"
    );

    const avatar = document.createElement("div");

    avatar.classList.add(
        "message-avatar"
    );

    avatar.setAttribute(
        "aria-hidden",
        "true"
    );

    avatar.textContent = "👤";


    const conteudo = document.createElement("div");

    conteudo.classList.add(
        "message-content"
    );


    const autor = document.createElement("span");

    autor.classList.add(
        "message-author"
    );

    autor.textContent = "Você";


    const textoMensagem = document.createElement("p");

    textoMensagem.textContent = texto;


    conteudo.appendChild(autor);
    conteudo.appendChild(textoMensagem);

    mensagem.appendChild(avatar);
    mensagem.appendChild(conteudo);

    chat.appendChild(mensagem);

    rolarChat();

}


/* =========================================================
   ADICIONAR RESPOSTA DO ASSISTENTE
   ========================================================= */

function adicionarResposta(resposta, fontes = []) {

    const mensagem = document.createElement("div");

    mensagem.classList.add(
        "message",
        "assistant"
    );


    /* Avatar */

    const avatar = document.createElement("div");

    avatar.classList.add(
        "message-avatar"
    );

    avatar.setAttribute(
        "aria-hidden",
        "true"
    );

    avatar.textContent = "🤖";


    /* Conteúdo */

    const conteudo = document.createElement("div");

    conteudo.classList.add(
        "message-content"
    );


    /* Autor */

    const autor = document.createElement("span");

    autor.classList.add(
        "message-author"
    );

    autor.textContent = "VittaMov";


    /* Texto */

    const texto = document.createElement("p");

    texto.textContent = resposta;


    conteudo.appendChild(autor);
    conteudo.appendChild(texto);


    /* =====================================================
       FONTES CONSULTADAS
    ===================================================== */

    if (
        Array.isArray(fontes) &&
        fontes.length > 0
    ) {

        const fontesContainer =
            document.createElement("div");

        fontesContainer.classList.add(
            "sources"
        );


        const titulo =
            document.createElement("strong");

        titulo.textContent =
            "Fontes consultadas:";


        const lista =
            document.createElement("ul");


        fontes.forEach((fonte) => {

            const item =
                document.createElement("li");

            item.textContent = fonte;

            lista.appendChild(item);

        });


        fontesContainer.appendChild(titulo);
        fontesContainer.appendChild(lista);

        conteudo.appendChild(
            fontesContainer
        );
    }


    mensagem.appendChild(avatar);
    mensagem.appendChild(conteudo);

    chat.appendChild(mensagem);

    rolarChat();

}


/* =========================================================
   INDICADOR DE CARREGAMENTO
   ========================================================= */

function adicionarLoading() {

    const mensagem = document.createElement("div");

    mensagem.classList.add(
        "message",
        "assistant",
        "loading"
    );


    const avatar = document.createElement("div");

    avatar.classList.add(
        "message-avatar"
    );

    avatar.setAttribute(
        "aria-hidden",
        "true"
    );

    avatar.textContent = "🤖";


    const conteudo = document.createElement("div");

    conteudo.classList.add(
        "message-content"
    );


    const autor = document.createElement("span");

    autor.classList.add(
        "message-author"
    );

    autor.textContent = "VittaMov";


    const texto = document.createElement("p");

    texto.textContent =
        "Buscando informações...";


    conteudo.appendChild(autor);
    conteudo.appendChild(texto);

    mensagem.appendChild(avatar);
    mensagem.appendChild(conteudo);

    chat.appendChild(mensagem);

    rolarChat();

    return mensagem;
}


/* =========================================================
   ROLAR CHAT PARA A ÚLTIMA MENSAGEM
   ========================================================= */

function rolarChat() {

    chat.scrollTo({
        top: chat.scrollHeight,
        behavior: "smooth"
    });

}


/* =========================================================
   ENVIAR PERGUNTA
   ========================================================= */

async function enviarPergunta(pergunta = null) {

    const texto =
        pergunta ||
        questionInput.value.trim();


    if (!texto) {
        return;
    }


    /* =====================================================
       MOSTRAR PERGUNTA
    ===================================================== */

    adicionarMensagemUsuario(texto);


    /* Limpar campo */

    questionInput.value = "";


    /* Desabilitar interface */

    sendButton.disabled = true;
    questionInput.disabled = true;


    /* Mostrar carregamento */

    const loading =
        adicionarLoading();


    try {

        const response =
            await fetch(API_PERGUNTAR, {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    pergunta: texto
                })

            });


        /* =================================================
           VALIDAR RESPOSTA HTTP
        ================================================= */

        if (!response.ok) {

            throw new Error(
                `Erro HTTP ${response.status}`
            );

        }


        const dados =
            await response.json();


        /* Remover loading */

        loading.remove();


        /* =================================================
           EXIBIR RESPOSTA
        ================================================= */

        adicionarResposta(
            dados.resposta ||
            "Não foi possível obter uma resposta.",
            dados.fontes || []
        );


    } catch (erro) {

        console.error(
            "Erro ao consultar a API:",
            erro
        );


        /* Remover loading */

        loading.remove();


        /* Mensagem de erro */

        adicionarResposta(
            "Não foi possível conectar ao assistente VittaMov. Verifique se a API está em execução.",
            []
        );

    } finally {

        /* Reativar interface */

        sendButton.disabled = false;
        questionInput.disabled = false;

        questionInput.focus();

    }

}


/* =========================================================
   FORMULÁRIO
   ========================================================= */

if (questionForm) {

    questionForm.addEventListener(
        "submit",
        function (evento) {

            evento.preventDefault();

            enviarPergunta();

        }
    );

}


/* =========================================================
   PERGUNTAS SUGERIDAS
   ========================================================= */

suggestionButtons.forEach(
    (button) => {

        button.addEventListener(
            "click",
            function () {

                const pergunta =
                    this.textContent.trim();

                questionInput.value =
                    pergunta;

                enviarPergunta(
                    pergunta
                );

            }
        );

    }
);


/* =========================================================
   INICIALIZAÇÃO
   ========================================================= */

document.addEventListener(
    "DOMContentLoaded",
    function () {

        verificarAPI();

        questionInput.focus();

    }
);

