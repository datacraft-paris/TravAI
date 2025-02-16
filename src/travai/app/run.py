import streamlit as st
from PIL import Image
import json
import os
import chromadb
from copy import deepcopy
from dotenv import load_dotenv
import base64
from pydantic import BaseModel
from travai.model.inference import get_structured_answer, get_client
from datetime import datetime
from travai.backend.vector_db.query import query_food
from travai.backend.services.meal_service import create_meal
from travai.backend.services.patient_service import get_patient_by_email, authenticate_user
from travai.backend.services.detected_ingredient_service import create_detected_ingredient
from travai.backend.services.modified_ingredient_service import create_modified_ingredient, update_modified_ingredient, delete_modified_ingredient
import torch


st.set_page_config(layout="wide")
torch.classes.__path__ = []
# region Pydantic Models

class Ingredient(BaseModel):
    """
    Represents an ingredient used in a dish.

    Attributes:
        ingredient_name (str): The name of the ingredient.
        quantity_grams (float): The quantity of the ingredient in grams.
    """
    ingredient_name: str
    quantity_grams: float

class Dish(BaseModel):
    """
    Represents a dish composed of multiple ingredients.

    Attributes:
        dish_name (Optional[str]): The name of the dish (can be None).
        ingredients (List[Ingredient]): A list of ingredients required to prepare the dish.
            Must contain at least one ingredient.
    """
    dish_name: str
    ingredients: list[Ingredient]

class DishSuggestion(BaseModel):
    """
    Represents a suggestion of possible dishes.

    Attributes:
        possible_dishes (List[Dish]): A list of suggested dishes.
    """
    possible_dishes: list[Dish]

def save_uploaded_image(uploaded_file):
    """
    Saves an uploaded image to the assets folder and returns the file path.
    :param uploaded_file: The uploaded file from Streamlit
    :return: The file path of the saved image
    """
    ASSET_DIR = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(ASSET_DIR, exist_ok=True)
    if uploaded_file is not None:
        # Generate a unique filename
        file_extension = uploaded_file.name.split('.')[-1]
        filename = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        file_path = os.path.join(ASSET_DIR, filename)

        # Save the file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        return file_path  # Return the saved file path
    return None

#region Journal Update Function

def update_journal(vlm_result: dict, uploaded_image, timestamp: datetime) -> None:
    """
    Extracts information from the VLM result and adds a new entry to the journal.
    """
    extracted_ingredients = vlm_result.get("ingredients", [])
    dish_name = vlm_result.get("dish_name", "Unknown Meal")  # <-- We retrieve the dish name here

    new_entry = {
        "datetime": timestamp.isoformat(),
        "photo": uploaded_image,
        "extracted_ingredients": extracted_ingredients,
        "dish_name": dish_name  # <-- We store it in the entry
    }
    if "journal" not in st.session_state:
        st.session_state["journal"] = []

    st.session_state["journal"].append(new_entry)



#region meal_analysis_page

def show_meal_analysis_page():
    """
    Renders the Meal Analysis page:
    - Lets the user upload an image
    - Analyzes it via the LLM
    - Lets the user edit the dish name & ingredients (CRUD)
    - Updates the journal on demand
    """
    st.title("Meal Analysis (Med)")
    st.write("Upload an image of your meal to analyze its content.")

    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Display the uploaded image
        try:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
        except Exception as e:
            st.error("Error opening the image. Please try another file.")
            st.error(str(e))
            return

        if st.button("Analyze Image"):
            with st.spinner("Analyzing image..."):
                try:
                    raw_result = get_structured_answer(
                        client=st.session_state["client"],
                        model_name="pixtral-12b-2409",
                        prompt=(
                            "Describe the list of ingredients required to make this dish "
                            "using the classes Ingredient and Dish"
                        ),
                        base64_image=base64.b64encode(uploaded_file.getvalue()).decode("utf-8"),
                        response_format=DishSuggestion,
                    )
                    # Convert the result (JSON string) to a Python dict
                    parsed_result = json.loads(raw_result)['possible_dishes']
                    st.session_state['parsed_result'] = parsed_result
                    dish2id = {dish['dish_name']: i for i, dish in enumerate(parsed_result)}
                    st.session_state['dish2id'] = dish2id
                    st.success("Analysis complete!")

                    # Initialize session state for dish name and ingredients
                except Exception as e:
                    st.error("An error occurred during image analysis.")
                    st.error(str(e))
                    return
        if 'dish2id' in st.session_state:
            choice = st.radio(
                label="Choose the right dish from the selection",
                options=st.session_state['dish2id'].keys(),
                index=None
            ) if len(st.session_state['dish2id']) > 1 else st.session_state['parsed_result'][0]['dish_name']
            patient = get_patient_by_email(email=st.session_state["email"])
            meal = create_meal(
                patient_id=patient.patient_id,
                date_start=datetime.now(),
                image_path=save_uploaded_image(uploaded_file=uploaded_file),
                name=choice,
            )
            # Here vectorization + detected food + copy modified food = detected food at this time
            if choice is not None:
                st.subheader("Edit Dish and Ingredients Before Saving")

                # Edit the dish name
                st.session_state["edit_dish_name"] = st.text_input(
                    "Dish Name",
                    value=choice,
                )

                # Editable table for ingredients
                ingredients_data = st.session_state['parsed_result'][st.session_state['dish2id'][choice]].get('ingredients')
                print([ingredient['ingredient_name'] for ingredient in ingredients_data])
                if 'chroma_db_client' not in st.session_state:
                    st.session_state['chroma_db_client'] = chromadb.PersistentClient(path="/Users/raphael/TravAI/chroma_db/")
                closest_food_ids, closest_food_names, closest_calories = query_food(client=st.session_state['chroma_db_client'], foods=deepcopy([ingredient['ingredient_name'] for ingredient in ingredients_data]))
                for food_id, food_name, calories, quantity in zip(closest_food_ids, closest_food_names, closest_calories, [ingredient['quantity_grams'] for ingredient in ingredients_data]):
                    create_detected_ingredient(
                        meal_id=meal.meal_id,
                        ingredient_id=food_id,
                        ingredient_name=food_name,
                        quantity_grams=quantity
                    )
                    create_modified_ingredient(detected_ingredient_id=food_id, quantity_grams=quantity)
                # Use a while loop to safely remove items without messing up indexing
                i = 0
                while i < len(ingredients_data):
                    row = ingredients_data[i]
                    c1, c2, c3 = st.columns([3, 3, 1])
                    with c1:
                        new_name = st.text_input(
                            f"Ingredient Name {i}",
                            value=row["ingredient_name"],
                            key=f"name_{i}"
                        )
                    with c2:
                        new_qty = st.number_input(
                            f"Quantity (g) {i}",
                            value=float(row["quantity_grams"]),
                            step=1.0,
                            key=f"qty_{i}"
                        )
                        if new_qty != float(row["quantity_grams"]):
                            update_modified_ingredient(modified_ingredient_id=closest_food_ids[i], quantity_grams=new_qty)
                    with c3:
                        # Minus button to remove the row
                        remove_btn_label = f"Remove {i}"
                        if st.button("–", key=remove_btn_label):
                            delete_modified_ingredient(closest_food_ids[i])
                            ingredients_data.pop(i)
                            # Force a re-run so the row disappears immediately
                            st.rerun()

                    # Update the row with user inputs
                    row["ingredient_name"] = new_name
                    row["quantity_grams"] = new_qty

                    i += 1

                # Plus button to add a new ingredient
                if st.button("+ Add Ingredient"):
                    ingredients_data.append({
                        "ingredient_name": "",
                        "quantity_grams": 0
                    })
                    st.rerun()

                # 3) Once the user is happy, let them download or save to journal
                dish_data = {
                    "dish_name": choice,
                    "ingredients": ingredients_data
                }

                # Download updated JSON
                updated_json_str = json.dumps(dish_data, indent=4)
                st.download_button(
                    label="Download Updated JSON",
                    data=updated_json_str,
                    file_name="meal_analysis.json",
                    mime="application/json"
                )

                # Button to finalize and add to the journal
                if st.button("Save to Journal"):
                    # Modify modified food
                    # Save final data to journal
                    update_journal(dish_data, image, datetime.now())
                    st.info("Your meal analysis has been added to the journal.")
                    # Optionally clear or reset the editing data
                    del st.session_state['dish2id']
                    uploaded_file = None


#region history_page 

def show_history_page():
    """
    Renders the History page with the histogram and metrics displayed at the top,
    followed by the table of analyzed meals.
    """
    st.title("History")
    st.write("View the history of analyzed meals in a tabular format with a 'Voir plus' button to reveal ingredients.")

    # Afficher les métriques et l'histogramme uniquement s'il y a des entrées dans le journal
    if "journal" in st.session_state and st.session_state["journal"]:
        # --- Calcul de la quantité totale par repas ---
        total_grams_list = []
        for entry in st.session_state["journal"]:
            ingredients = entry.get("extracted_ingredients", [])
            total = sum(item.get("quantity_grams", 0) for item in ingredients)
            total_grams_list.append(total)

        # Créer un DataFrame avec un identifiant pour chaque repas
        import pandas as pd
        df_meals = pd.DataFrame({
            "Repas": [f"Repas {i+1}" for i in range(len(total_grams_list))],
            "Quantité (g)": total_grams_list
        })

        # Créer le graphique à barres avec Altair : 
        # - x : le repas (catégoriel)
        # - y : la quantité totale consommée
        import altair as alt
        bar_chart = alt.Chart(df_meals).mark_bar(opacity=0.7).encode(
            x=alt.X("Repas:N", title="Repas"),
            y=alt.Y("Quantité (g):Q", title="Quantité Totale (g)")
        ).properties(
            title="Quantité mangée par repas",
            width=600,
            height=300
)

        st.altair_chart(bar_chart, use_container_width=True)

        # --- Affichage des métriques ---
        # Ici, on utilise des valeurs fixes pour l'instant
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Score de rigueur", value="10")
        with col2:
            st.metric(label="Taux d'objectif atteint", value="3")
        with col3:
            st.metric(label="Moyenne de la métrique traquée", value="5")
    else:
        st.info("No journal entries yet. Go to 'Meal Analysis' (or 'Take Photo' if patient) and analyze a meal.")

    st.write("---")  # Séparateur visuel entre les métriques/histogramme et le tableau

    # Si aucune entrée dans le journal, on arrête ici
    if "journal" not in st.session_state or not st.session_state["journal"]:
        return

    # ----- TABLEAU DES ENTRÉES DU JOURNAL -----
    # On crée un entête de tableau avec des colonnes
    header_col1, header_col2, header_col3, header_col4 = st.columns([2, 2, 2, 1])
    header_col1.write("**Date**")
    header_col2.write("**Meal Name**")
    header_col3.write("**Photo**")
    header_col4.write("")

    # Variable pour savoir quel repas développer pour voir les ingrédients
    if "show_ingredients_for" not in st.session_state:
        st.session_state["show_ingredients_for"] = None

    # Parcourir chaque entrée du journal et afficher une ligne par repas
    for i, entry in enumerate(st.session_state["journal"]):
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
        
        # 1) Date
        dt_str = entry["datetime"]  # chaîne ISO, par exemple "2025-02-15T19:49:05.326333"
        try:
            dt_obj = datetime.fromisoformat(dt_str)
            date_formatted = dt_obj.strftime("%d/%m/%Y %H:%M:%S")
        except ValueError:
            date_formatted = dt_str
        col1.write(date_formatted)

        # 2) Nom du repas
        dish_name = entry.get("dish_name", "Unknown Meal")
        col2.write(dish_name)

        # 3) Photo (thumbnail)
        photo = entry.get("photo")
        if photo:
            if isinstance(photo, Image.Image):
                col3.image(photo, width=80)
            else:
                try:
                    img = Image.open(photo)
                    col3.image(img, width=80)
                except:
                    col3.write("No image")
        else:
            col3.write("No image")

        # 4) Bouton "Voir plus"
        if col4.button("Voir plus", key=f"voir_plus_{i}"):
            if st.session_state["show_ingredients_for"] == i:
                st.session_state["show_ingredients_for"] = None  # Pour masquer si déjà affiché
            else:
                st.session_state["show_ingredients_for"] = i
            st.rerun()

        # Affichage des ingrédients si "Voir plus" est activé pour cette entrée
        if st.session_state["show_ingredients_for"] == i:
            st.write("**Ingredients:**")
            ingredients = entry.get("extracted_ingredients", [])
            st.table(ingredients)
            st.write("---")


#region Authentication Page

def show_authentication_page():
    """
    Displays a login form for email + password.
    If valid, sets session state accordingly and reruns.
    """
    st.title("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user, role = authenticate_user(email, password)
        if role is None:
            st.error("Invalid email or password. Please try again.")
        else:
            st.session_state["logged_in"] = True
            st.session_state["role"] = role
            st.session_state['email'] = email
            st.rerun()



#region Main

def main():
    load_dotenv()
    # Ensure we have a client
    if "client" not in st.session_state:
        st.session_state["client"] = get_client()

    # Ensure we have login info
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "role" not in st.session_state:
        st.session_state["role"] = None

    # If not logged in, show login
    if not st.session_state["logged_in"]:
        show_authentication_page()
    else:
        # If logged in, check role
        if st.session_state["role"] == "patient":
            # Patient has two tabs: Take Photo + History
            tab1, tab2 = st.tabs(["Take Photo", "History"])
            with tab1:
                show_meal_analysis_page()
            with tab2:
                show_history_page()

        elif st.session_state["role"] == "doctor":
            # Med sees only the History page
            show_history_page()
        else:
            st.error("Unknown role. Please log out and try again.")


if __name__ == "__main__":
    main()