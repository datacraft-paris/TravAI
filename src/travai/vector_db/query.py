import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Ensure persistent storage
client = chromadb.PersistentClient(path="./chroma_db")

# Create or retrieve collection
collection = client.get_or_create_collection("food_embeddings")

query_embedding = model.encode(["mushroom"], convert_to_tensor=True).tolist()

results = collection.query(
    query_embeddings=query_embedding, # Chroma will embed this for you
    n_results=5# how many results to return
)


english_names = [meta["alim_nom_en"] for meta in results["metadatas"][0]]

# Print clean output
print("\n🥗 Top Matching Foods for 'mushroom':")
for i, name in enumerate(english_names, 1):
    print(f"{i}. {name}")