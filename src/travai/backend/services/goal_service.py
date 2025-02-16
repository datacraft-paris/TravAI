from sqlalchemy.orm import Session
from travai.backend.database import SessionLocal
from travai.backend.models import Goal, Patient
from datetime import datetime

def create_goal(patient_id: int, date_start: datetime, date_end: datetime, calories_in_grams_per_day: float):
    """
    Creates a new goal and assigns it to a patient.

    :param patient_id: ID of the patient associated with the goal
    :param date_start: Start date of the goal
    :param date_end: End date of the goal
    :param calories_in_grams_per_day: Target daily calorie intake in grams
    :return: The created Goal object or None if an error occurs
    """
    session = SessionLocal()

    try:
        # Verify that the patient exists
        patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not patient:
            print("Patient ID does not exist.")
            return None

        # Create a new Goal object
        new_goal = Goal(
            patient_id=patient_id,
            date_start=date_start,
            date_end=date_end,
            calories_in_grams_per_day=calories_in_grams_per_day
        )

        # Add the goal to the database
        session.add(new_goal)
        session.commit()
        session.refresh(new_goal)  # Refresh instance with DB values

        print(f"Goal created: {new_goal.calories_in_grams_per_day} kcal/day for Patient ID {new_goal.patient_id}")
        return new_goal

    except Exception as e:
        session.rollback()
        print(f"Error while adding the goal: {e}")
        return None

    finally:
        session.close()


def get_goal_by_id(goal_id: int):
    """
    Retrieves a goal from the database using its ID.

    :param goal_id: The ID of the goal to retrieve
    :return: The Goal object if found, else None
    """
    session = SessionLocal()
    try:
        goal = session.query(Goal).filter(Goal.goal_id == goal_id).first()
        if goal:
            print(f"Goal found: {goal.calories_in_grams_per_day} kcal/day (Goal ID: {goal.goal_id})")
        return goal
    except Exception as e:
        print(f"Error retrieving goal: {e}")
        return None
    finally:
        session.close()


def get_goals_by_patient(patient_id: int):
    """
    Retrieves all goals for a specific patient.

    :param patient_id: The ID of the patient whose goals are to be retrieved
    :return: A list of Goal objects or an empty list if none found
    """
    session = SessionLocal()
    try:
        goals = session.query(Goal).filter(Goal.patient_id == patient_id).all()
        print(f"{len(goals)} goals found for Patient ID {patient_id}")
        return goals
    except Exception as e:
        print(f"Error retrieving goals: {e}")
        return []
    finally:
        session.close()


def update_goal(goal_id: int, date_start: datetime = None, date_end: datetime = None, calories_in_grams_per_day: float = None):
    """
    Updates details of a goal in the database.

    :param goal_id: The ID of the goal to update
    :param date_start: (Optional) New start date
    :param date_end: (Optional) New end date
    :param calories_in_grams_per_day: (Optional) New target calorie intake per day
    :return: The updated Goal object or None if not found
    """
    session = SessionLocal()
    try:
        goal = session.query(Goal).filter(Goal.goal_id == goal_id).first()
        if not goal:
            print("Goal not found.")
            return None

        # Update fields if new values are provided
        if date_start:
            goal.date_start = date_start
        if date_end:
            goal.date_end = date_end
        if calories_in_grams_per_day is not None:
            goal.calories_in_grams_per_day = calories_in_grams_per_day

        session.commit()
        session.refresh(goal)

        print(f"Goal updated: {goal.calories_in_grams_per_day} kcal/day (Goal ID: {goal.goal_id})")
        return goal

    except Exception as e:
        session.rollback()
        print(f"Error updating goal: {e}")
        return None
    finally:
        session.close()


def delete_goal(goal_id: int):
    """
    Deletes a goal from the database.

    :param goal_id: The ID of the goal to delete
    :return: True if deleted successfully, False otherwise
    """
    session = SessionLocal()
    try:
        goal = session.query(Goal).filter(Goal.goal_id == goal_id).first()
        if not goal:
            print("Goal not found.")
            return False

        session.delete(goal)
        session.commit()

        print(f"Goal deleted (ID: {goal.goal_id})")
        return True

    except Exception as e:
        session.rollback()
        print(f"Error deleting goal: {e}")
        return False
    finally:
        session.close()