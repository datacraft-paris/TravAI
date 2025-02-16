import chromadb
from sentence_transformers import SentenceTransformer


def get_model() -> SentenceTransformer:
    return SentenceTransformer('paraphrase-MiniLM-L6-v2')

def query_food(client: chromadb.PersistentClient, foods: list[str]):
    model = get_model()
    # Ensure persistent storage
    # Create or retrieve collection
    collection = client.get_or_create_collection("food_embeddings")

    query_embedding = model.encode(foods, convert_to_tensor=True).tolist()
    results = collection.query(
        query_embeddings=query_embedding, # Chroma will embed this for you
        n_results=5# how many results to return
    )
    names = [meta[0]["alim_nom_en"] for meta in results["metadatas"]]
    ids = [idx[0] for idx in results['ids']]
    calories = [cal[0]['Energie_kcal_100g'] for cal in results['metadatas']]
    return ids, names, calories
