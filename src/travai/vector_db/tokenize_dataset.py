import pandas as pd
import json

food_dataset = pd.read_csv('/Users/datacraft-marc/Documents/Code/CSV_hackathon/Table-Ciqual-2020_processed_final.csv')

tokenized_corpus = [doc.split(" ") for doc in food_dataset['alim_nom_en']]

# Save as JSON
with open("tokenized_corpus.json", "w", encoding="utf-8") as f:
    json.dump(tokenized_corpus, f, ensure_ascii=False, indent=4)

print("Tokenized corpus saved as JSON!")
