import streamlit as st
from PIL import Image
import json
from dotenv import load_dotenv
import base64
from pydantic import BaseModel
from datetime import datetime

from travai.model.inference import get_structured_answer, get_client

st.set_page_config(layout="wide")


# region Pydantic Models

class Ingredient(BaseModel):
    ingredient_name: str
    quantity_grams: float

class Dish(BaseModel):
    dish_name: str | None
    ingredients: list[Ingredient]


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

def update_journal(vlm_result: dict, uploaded_image, timestamp: datetime) -> None:
    """
    Extracts information from the VLM result and adds a new entry to the journal.
    """
    extracted_ingredients = vlm_result.get("ingredients", [])
    new_entry = {
        "datetime": timestamp.isoformat(),
        "photo": uploaded_image,
        "extracted_ingredients": extracted_ingredients
    }

    if "journal" not in st.session_state:
        st.session_state["journal"] = []
    st.session_state["journal"].append(new_entry)



#region Meal Analysis & History

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

        # Editing UI if dish data is available
        if "edit_dish_name" in st.session_state and "edit_ingredients" in st.session_state:
            st.subheader("Edit Dish and Ingredients Before Saving")

            # Edit dish name
            st.session_state["edit_dish_name"] = st.text_input(
                "Dish Name",
                value=st.session_state["edit_dish_name"],
            )

            # Editable table for ingredients
            ingredients_data = st.session_state["edit_ingredients"]

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
                    remove_btn_label = f"Remove {i}"
                    if st.button("–", key=remove_btn_label):
                        ingredients_data.pop(i)
                        st.rerun()

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

            # Prepare final data
            dish_data = {
                "dish_name": st.session_state["edit_dish_name"],
                "ingredients": ingredients_data
            }

            # Save to Journal
            if st.button("Save to Journal"):
                update_journal(dish_data, image, datetime.now())
                st.info("Your meal analysis has been added to the journal.")
                # Clear editing state
                del st.session_state["edit_dish_name"]
                del st.session_state["edit_ingredients"]


def show_history_page():
    """
    Renders the History page with improved display:
    - Shows the date in a friendlier format
    - Displays the actual image
    - Shows ingredients in a table
    """
    st.title("History")
    st.write("View the history of analyzed meals in a more detailed format.")

    # Check if there's any entry in the journal
    if "journal" not in st.session_state or len(st.session_state["journal"]) == 0:
        st.info("No journal entries yet. Go to 'Meal Analysis' (or 'Take Photo' if patient) and analyze a meal to populate the history.")
        return

    # Loop through each entry in the journal
    for i, entry in enumerate(st.session_state["journal"], start=1):
        st.subheader(f"Entry {i}")

        # 1) Format and display the date
        # The entry stores "datetime" as an ISO string (e.g., "2025-02-15T19:49:05.326333")
        # We can parse it into a Python datetime and reformat it nicely
        dt_str = entry["datetime"]  # e.g. "2025-02-15T19:49:05.326333"
        try:
            dt_obj = datetime.fromisoformat(dt_str)
            formatted_date = dt_obj.strftime("%d/%m/%Y %H:%M:%S")  # e.g. "15/02/2025 19:49:05"
        except ValueError:
            # If parsing fails for some reason, just use the raw string
            formatted_date = dt_str
        st.write(f"**Date:** {formatted_date}")

        # 2) Display the image
        # The entry["photo"] should be a PIL Image object or raw bytes
        # If you stored the PIL Image, we can show it directly with st.image
        photo = entry.get("photo")
        if photo:
            # If we stored the actual PIL Image object:
            if isinstance(photo, Image.Image):
                st.image(photo, caption="Meal Photo", use_container_width=True)
            else:
                # Otherwise, if we stored bytes, we can reconstruct a PIL image:
                try:
                    img = Image.open(photo)
                    st.image(img, caption="Meal Photo", use_container_width=True)
                except Exception:
                    st.write("Could not display the image.")
        else:
            st.write("No image found in this entry.")

        # 3) Display the extracted ingredients
        # If entry["extracted_ingredients"] is a list of dicts,
        # st.table can display them in a tabular format
        extracted_ingredients = entry.get("extracted_ingredients", [])
        if extracted_ingredients:
            st.write("**Extracted Ingredients:**")
            # Each dict might look like {"ingredient_name": "Tomato", "quantity_grams": 50}
            # st.table can handle a list of dicts directly
            st.table(extracted_ingredients)
        else:
            st.write("No ingredients found in this entry.")

        st.write("---")  # A horizontal rule for visual separation



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