import chromadb
import json
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

# Ensure persistent storage
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection("food_embeddings")

with open("tokenized_corpus.json", "r", encoding="utf-8") as f:
    tokenized_corpus = json.load(f)

bm25 = BM25Okapi(tokenized_corpus)

def hybrid_search(query, top_k=5):
    # BM25 Search
    tokenized_query = query.split(" ")
    bm25_scores = bm25.get_scores(tokenized_query)
    bm25_top_k = bm25_scores.argsort()[-top_k:][::-1]
    bm25_ids = [str(i) for i in bm25_top_k]

    # Vector Search
    query_embedding = model.encode([query], convert_to_tensor=True)
    vector_results = collection.query(query_embeddings=query_embedding.tolist(), n_results=top_k)
    vector_ids = vector_results['ids'][0]

    combined_ids = list(set(bm25_ids).union(set(vector_ids)))

    final_results = collection.get(combined_ids)

    food_info = [
        (meta["alim_nom_en"], meta.get("Energie_kcal_100g", "N/A"))
        for meta in final_results["metadatas"]
    ]

    return food_info

query = "bacon"

results = hybrid_search(query=query, top_k=5)

print(f"\n🍝 Top Matching Foods for {query} : ")
for i, name in enumerate(results, 1):
    print(f"{i}. {name}")
