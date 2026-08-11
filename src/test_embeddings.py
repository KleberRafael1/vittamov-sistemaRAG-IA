from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings


load_dotenv()


embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)


texto = "A Clínica VittaMov oferece fisioterapia ortopédica."


vetor = embeddings.embed_query(texto)


print("=" * 60)
print("VITTAMOV — TESTE DE EMBEDDINGS")
print("=" * 60)

print(f"\nTexto: {texto}")
print(f"Dimensão do vetor: {len(vetor)}")

print("\nPrimeiros valores:")
print(vetor[:10])

print("\n" + "=" * 60)
print("✅ Embedding gerado com sucesso!")
print("=" * 60)