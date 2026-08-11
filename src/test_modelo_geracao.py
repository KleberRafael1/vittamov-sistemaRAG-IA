import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

client = genai.Client(api_key=API_KEY)

modelos = [
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.6-flash",
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-2.0-flash-lite",
]

print("\nVITTAMOV — TESTE DE MODELOS DE GERAÇÃO")
print("=" * 60)

for modelo in modelos:
    print(f"\nTestando: {modelo}")

    try:
        resposta = client.models.generate_content(
            model=modelo,
            contents="Responda apenas: OK"
        )

        print("STATUS: FUNCIONOU")
        print("RESPOSTA:", resposta.text)

    except Exception as e:
        print("STATUS: ERRO")
        print(str(e)[:500])

print("\n" + "=" * 60)
print("TESTE CONCLUÍDO")