import streamlit as st
from PIL import Image
import json
from dotenv import load_dotenv
import base64
from pydantic import BaseModel
from travai.model.inference import get_structured_answer, get_client
from datetime import datetime

st.set_page_config(layout="wide")

class Ingredient(BaseModel):
    ingredient_name: str
    quantity_grams: float

class Dish(BaseModel):
    dish_name: str | None
    ingredients: list[Ingredient]

def update_journal(vlm_result: dict, uploaded_image, timestamp: datetime) -> None:

    extracted_ingredients = vlm_result.get("ingredients", [])

    new_entry = {
        "datetime": timestamp.isoformat(),
        "photo": uploaded_image,  
        "extracted_ingredients": extracted_ingredients
    }

    # Initialize journal if it doesn't exist yet
    if "journal" not in st.session_state:
        st.session_state["journal"] = []

    # Append the new entry
    st.session_state["journal"].append(new_entry)


def show_meal_analysis_page():
    
    """
    Renders the Meal Analysis page:
    - Lets the user upload an image
    - Analyzes it via the LLM
    - Lets the user edit the dish name & ingredients (CRUD)
    - Updates the journal on demand
    """
    st.title("Meal Analysis")
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
                    # Call the LLM / VLM
                    raw_result = get_structured_answer(
                        client=st.session_state["client"],
                        model_name="pixtral-12b-2409",
                        prompt="Describe the list of ingredients required to make this dish using the classes Ingredient and Dish",
                        base64_image=base64.b64encode(uploaded_file.getvalue()).decode("utf-8"),
                        response_format=Dish,
                    )
                    # Convert the result (JSON string) to a Python dict
                    parsed_result = json.loads(raw_result)

                    st.success("Analysis complete!")
                    
                    # Initialize session state for dish name and ingredients
                    st.session_state["edit_dish_name"] = parsed_result.get("dish_name", "No dish name provided")
                    st.session_state["edit_ingredients"] = parsed_result.get("ingredients", [])

                except Exception as e:
                    st.error("An error occurred during image analysis.")
                    st.error(str(e))
                    return

        if "edit_dish_name" in st.session_state and "edit_ingredients" in st.session_state:
            st.subheader("Edit Dish and Ingredients Before Saving")

            # Edit the dish name
            st.session_state["edit_dish_name"] = st.text_input(
                "Dish Name",
                value=st.session_state["edit_dish_name"],
            )

            # Editable table for ingredients
            ingredients_data = st.session_state["edit_ingredients"]

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
                with c3:
                    # Minus button to remove the row
                    remove_btn_label = f"Remove {i}"
                    if st.button("–", key=remove_btn_label):
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
                "dish_name": st.session_state["edit_dish_name"],
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
                # Save final data to journal
                update_journal(dish_data, image, datetime.now())
                st.info("Your meal analysis has been added to the journal.")
                # Optionally clear or reset the editing data
                del st.session_state["edit_dish_name"]
                del st.session_state["edit_ingredients"]


def show_history_page():
    st.title("History")
    st.write("View and edit the history of analyzed meals.")

    if "journal" not in st.session_state or len(st.session_state["journal"]) == 0:
        st.info("No journal entries yet. Go to 'Meal Analysis' and analyze a meal to populate the history.")
        return

    table_data = []
    for entry in st.session_state["journal"]:
        table_data.append({
            "datetime": entry["datetime"],
            "photo": "Image data (not displayed)",
            "extracted_ingredients": entry["extracted_ingredients"],
        })

    # Afficher les données sous forme de tableau
    st.data_editor(table_data)


def main():
    """
    Main function that handles page navigation and renders the selected page.
    """
    load_dotenv()
    st.session_state['client'] = get_client()
    load_dotenv()

    # Create two tabs at the top
    tab1, tab2 = st.tabs(["Meal Analysis", "History"])

    with tab1:
        show_meal_analysis_page()

    with tab2:
        show_history_page()


if __name__ == "__main__":
    main()