import streamlit as st
from PIL import Image
import json
from dotenv import load_dotenv
import base64
from pydantic import BaseModel, Field
from travai.model.inference import get_structured_answer, get_client
from datetime import datetime

from travai.model.inference import get_structured_answer, get_client

st.set_page_config(layout="wide")


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



#region Simulated Credential Storage

MED_CREDENTIALS = {
    "doctor@hospital.com": "med123",
}
PATIENT_CREDENTIALS = {
    "john.doe@example.com": "patient123",
}



#region Check Credentials

def check_credentials(email: str, password: str) -> str | None:
    """
    Returns "med" if the email/password is in the MED_CREDENTIALS,
    "patient" if in PATIENT_CREDENTIALS, or None if invalid.
    """
    # Check med
    if email in MED_CREDENTIALS and MED_CREDENTIALS[email] == password:
        return "med"
    # Check patient
    if email in PATIENT_CREDENTIALS and PATIENT_CREDENTIALS[email] == password:
        return "patient"
    return None


#region Journal Update Function


#region Simulated Credential Storage

MED_CREDENTIALS = {
    "doctor@hospital.com": "med123",
}
PATIENT_CREDENTIALS = {
    "john.doe@example.com": "patient123",
}

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
                        model_name="gpt-4o",
                        prompt=(
                            "Describe the list of ingredients required to make this dish "
                            "using the classes Ingredient and Dish"
                        ),
                        base64_image=base64.b64encode(uploaded_file.getvalue()).decode("utf-8"),
                        response_format=DishSuggestion,
                    )
                    print(raw_result)
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
            if choice is not None:
                st.subheader("Edit Dish and Ingredients Before Saving")

                # Edit the dish name
                st.session_state["edit_dish_name"] = st.text_input(
                    "Dish Name",
                    value=choice,
                )

                # Editable table for ingredients
                ingredients_data = st.session_state['parsed_result'][st.session_state['dish2id'][choice]].get('ingredients')

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
                    # Save final data to journal
                    update_journal(dish_data, image, datetime.now())
                    st.info("Your meal analysis has been added to the journal.")
                    # Optionally clear or reset the editing data
                    del st.session_state['dish2id']
                    uploaded_file = None


#region history_page 

def show_history_page():
    """
    Renders the History page in a tabular layout:
    | Date                | Meal Name       | Photo (thumbnail)    | Voir plus |
    and displays ingredients below the row if the user clicks 'Voir plus'.
    """
    st.title("History")
    st.write("View the history of analyzed meals in a tabular format with a 'Voir plus' button to reveal ingredients.")

    # Check if there's any entry in the journal
    if "journal" not in st.session_state or not st.session_state["journal"]:
        st.info("No journal entries yet. Go to 'Meal Analysis' (or 'Take Photo' if patient) and analyze a meal.")
        return

    # Create a place to store which row's ingredients to show
    if "show_ingredients_for" not in st.session_state:
        st.session_state["show_ingredients_for"] = None

    # ----- TABLE HEADER -----
    # We'll use columns to create a row for the headers
    header_col1, header_col2, header_col3, header_col4 = st.columns([2, 2, 2, 1])
    header_col1.write("**Date**")
    header_col2.write("**Meal Name**")
    header_col3.write("**Photo**")
    header_col4.write("")

    # Loop through each journal entry and display one row per entry
    for i, entry in enumerate(st.session_state["journal"]):
        col1, col2, col3, col4 = st.columns([2, 2, 2, 1])

        # 1) Date
        dt_str = entry["datetime"]  # ISO string (e.g. 2025-02-15T19:49:05.326333)
        try:
            dt_obj = datetime.fromisoformat(dt_str)
            date_formatted = dt_obj.strftime("%d/%m/%Y %H:%M:%S")
        except ValueError:
            # Fallback if parsing fails
            date_formatted = dt_str
        col1.write(date_formatted)

        # 2) Meal Name
        dish_name = entry.get("dish_name", "Unknown Meal")
        col2.write(dish_name)

        # 3) Photo (thumbnail)
        photo = entry.get("photo")
        if photo:
            # If you stored a PIL Image object:
            if isinstance(photo, Image.Image):
                col3.image(photo, width=80)
            else:
                # Otherwise, if you stored bytes, try converting to a PIL image
                try:
                    img = Image.open(photo)
                    col3.image(img, width=80)
                except:
                    col3.write("No image")
        else:
            col3.write("No image")

        # 4) Voir plus button
        if col4.button("Voir plus", key=f"voir_plus_{i}"):
            # Record which entry we want to see ingredients for, then re-run
            if st.session_state["show_ingredients_for"] == i:
                # If clicked again, hide it
                st.session_state["show_ingredients_for"] = None
            else:
                st.session_state["show_ingredients_for"] = i
            st.rerun()

        # If this row's "Voir plus" is active, display ingredients below
        if st.session_state["show_ingredients_for"] == i:
            st.write("**Ingredients:**")
            ingredients = entry.get("extracted_ingredients", [])
            st.table(ingredients)
            st.write("---")  # a horizontal rule to separate entries


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
        role = check_credentials(email, password)
        if role is None:
            st.error("Invalid email or password. Please try again.")
        else:
            st.session_state["logged_in"] = True
            st.session_state["role"] = role
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

        elif st.session_state["role"] == "med":
            # Med sees only the History page
            show_history_page()
        else:
            st.error("Unknown role. Please log out and try again.")


if __name__ == "__main__":
    main()