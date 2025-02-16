import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb

food_dataset = pd.read_csv('src/travai/backend/vector_db/Table-Ciqual-2020_processed_final.csv')

print("Data loaded 🍔")

# Creating embeddings
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
embeddings = model.encode(food_dataset['alim_nom_en'].tolist(), convert_to_tensor=True)



# Initialize Chroma client
client = chromadb.PersistentClient(path="./chroma_db")

# Delete the collection if it already exists
# client.delete_collection('food_embeddings')
# print(f"Deleted existing collection: {'food_embeddings'}")


collection = client.create_collection('food_embeddings')

# Create IDs
ids = [str(i) for i in range(len(food_dataset))]

print("Adding data to ChromaDB...")

# Insert data into Chroma
collection.add(embeddings=embeddings.tolist(),
               documents=food_dataset['alim_nom_en'].tolist(),
               ids=ids,
               metadatas=[
                   {
                       "alim_grp_code": grp_code,  # Group code
                       "alim_ssgrp_code": ssgrp_code,  # Sub-group code
                       "alim_ssssgrp_code": ssssgrp_code,  # Sub-sub-group code
                       "alim_grp_nom_fr": grp_name_fr,  # Group name in French
                       "alim_ssgrp_nom_fr": ssgrp_name_fr,  # Sub-group name in French
                       "alim_code": alim_code,  # Food code
                       "alim_nom_fr": alim_nom_fr,  # Food name in French
                       "alim_nom_en": alim_nom_en,  # Food name in English
                       "Energie_kcal_100g": energy_kcal  # Energy value (kcal per 100g)
                   }
                   for
                   grp_code, ssgrp_code, ssssgrp_code, grp_name_fr, ssgrp_name_fr, alim_code, alim_nom_fr, alim_nom_en, energy_kcal
                   in zip(
                       food_dataset['alim_grp_code'],
                       food_dataset['alim_ssgrp_code'],
                       food_dataset['alim_ssssgrp_code'],
                       food_dataset['alim_grp_nom_fr'],
                       food_dataset['alim_ssgrp_nom_fr'],
                       food_dataset['alim_code'],
                       food_dataset['alim_nom_fr'],
                       food_dataset['alim_nom_en'],
                       food_dataset['Energie (kcal/100 g)']
                   )
               ]
               )
print("Data added to ChromaDB 🚀")


