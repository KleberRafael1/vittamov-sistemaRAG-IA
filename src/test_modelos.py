from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("GOOGLE_API_KEY não encontrada.")

client = genai.Client(api_key=api_key)

print("\nMODELOS DISPONÍVEIS PARA ESTA API KEY\n")
print("=" * 70)

for model in client.models.list():
    print(model.name)

print("=" * 70)