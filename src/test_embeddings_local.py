from langchain_huggingface import HuggingFaceEmbeddings


print("=" * 60)
print("VITTAMOV — TESTE DE EMBEDDINGS LOCAIS")
print("=" * 60)

print("\n⏳ Carregando modelo...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

texto = "A Clínica VittaMov oferece fisioterapia ortopédica."

vetor = embeddings.embed_query(texto)

print(f"\nTexto: {texto}")
print(f"Dimensão do vetor: {len(vetor)}")

print("\nPrimeiros valores:")
print(vetor[:10])

print("\n" + "=" * 60)
print("✅ Embedding local gerado com sucesso!")
print("=" * 60)