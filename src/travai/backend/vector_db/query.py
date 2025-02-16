import chromadb
from sentence_transformers import SentenceTransformer


def get_model() -> SentenceTransformer:
    return SentenceTransformer('paraphrase-MiniLM-L6-v2')

def query_food(model: SentenceTransformer, foods: list[str]):
    # Ensure persistent storage
    client = chromadb.PersistentClient(path="./chroma_db")

    # Create or retrieve collection
    collection = client.get_or_create_collection("food_embeddings")

    query_embedding = model.encode(foods, convert_to_tensor=True).tolist()

    results = collection.query(
        query_embeddings=query_embedding, # Chroma will embed this for you
        n_results=5 # how many results to return
    )
    return [meta["alim_nom_en"] for meta in results["metadatas"][0]]
