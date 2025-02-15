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
    - Analyzes it via VLM
    - Updates the journal
    """
    st.title("Meal Analysis")
    st.write("Upload an image of your meal to analyze its content.")

    # Image upload
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

        # Analyze the image when user clicks the button
        if st.button("Analyze Image"):
            with st.spinner("Analyzing image..."):
                try:
                    # Call the VLM to analyze
                    vlm_result = get_structured_answer(
                        client=st.session_state['client'],
                        model_name="pixtral-12b-2409",
                        prompt="Describe the list of ingredients required to make this dish using the classes Ingredient and Dish",
                        base64_image=base64.b64encode(uploaded_file.getvalue()).decode('utf-8'),
                        response_format=Dish,
                    )
                    vlm_result = json.loads(vlm_result)
                    # Display the raw JSON result
                    st.success("Analysis complete!")
                    st.json(vlm_result)

                    # Optionally let user download the JSON
                    vlm_json_str = json.dumps(vlm_result, indent=4)
                    st.download_button(
                        label="Download JSON",
                        data=vlm_json_str,
                        file_name="meal_analysis.json",
                        mime="application/json"
                    )

                    # Update the journal with the result
                    update_journal(vlm_result, image, datetime.now())
                    st.info("Your meal analysis has been added to the journal.")

                except Exception as e:
                    st.error("An error occurred during image analysis.")
                    st.error(str(e))


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
    st.sidebar.title("Navigation")
    page_choice = st.sidebar.radio("Go to", ["Meal Analysis", "History"])

    if page_choice == "Meal Analysis":
        show_meal_analysis_page()
    elif page_choice == "History":
        show_history_page()


if __name__ == "__main__":
    main()