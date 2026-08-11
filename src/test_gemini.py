from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash"
)

response = model.invoke(
    "Responda apenas: Conexão com o Gemini funcionando."
)

print(response.content)