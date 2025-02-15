from sqlalchemy.orm import Session
from database import SessionLocal
from models import Doctor, Patient

def create_doctor(first_name: str, last_name: str, email: str, password: str):
    """
    Creates a new doctor and adds them to the database.

    :param first_name: Doctor's first name
    :param last_name: Doctor's last name
    :param email: Doctor's email (must be unique)
    :param password: Password (should be hashed before storage)
    :return: The created doctor object or None if an error occurs
    """
    session = SessionLocal()

    try:
        # Check if a doctor with the given email already exists
        existing_doctor = session.query(Doctor).filter(Doctor.email == email).first()
        if existing_doctor:
            print("A doctor with this email already exists.")
            return None

        # Create a new Doctor object
        new_doctor = Doctor(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password  # TODO: Implement password hashing before storing
        )

        # Add the doctor to the database
        session.add(new_doctor)
        session.commit()
        session.refresh(new_doctor)  # Refresh the instance with DB values

        print(f"Doctor created: {new_doctor.first_name} {new_doctor.last_name} ({new_doctor.email})")
        return new_doctor

    except Exception as e:
        session.rollback()  # Roll back in case of an error
        print(f"Error while adding the doctor: {e}")
        return None

    finally:
        session.close()  # Ensure session is closed properly


def get_doctor_by_email(email: str):
    """
    Retrieves a doctor from the database using their email.

    :param email: The email of the doctor to retrieve
    :return: The Doctor object if found, else None
    """
    session = SessionLocal()
    try:
        doctor = session.query(Doctor).filter(Doctor.email == email).first()
        if doctor:
            print(f"Doctor found: {doctor.first_name} {doctor.last_name} ({doctor.email})")
        return doctor
    except Exception as e:
        print(f"Error retrieving doctor: {e}")
        return None
    finally:
        session.close()


def update_doctor(email: str, first_name: str = None, last_name: str = None, password: str = None):
    """
    Updates doctor details in the database.

    :param email: The email of the doctor to update
    :param first_name: (Optional) New first name
    :param last_name: (Optional) New last name
    :param password: (Optional) New password (should be hashed before storage)
    :return: The updated doctor object or None if not found
    """
    session = SessionLocal()
    try:
        doctor = session.query(Doctor).filter(Doctor.email == email).first()
        if not doctor:
            print("Doctor not found.")
            return None

        # Update fields if new values are provided
        if first_name:
            doctor.first_name = first_name
        if last_name:
            doctor.last_name = last_name
        if password:
            doctor.password = password  # TODO: Implement password hashing before updating

        session.commit()
        session.refresh(doctor)

        print(f"Doctor updated: {doctor.first_name} {doctor.last_name}")
        return doctor

    except Exception as e:
        session.rollback()
        print(f"Error updating doctor: {e}")
        return None
    finally:
        session.close()


def delete_doctor(email: str):
    """
    Deletes a doctor from the database and unassigns all associated patients.

    :param email: The email of the doctor to delete
    :return: True if deleted successfully, False otherwise
    """
    session = SessionLocal()
    try:
        # Find the doctor by email
        doctor = session.query(Doctor).filter(Doctor.email == email).first()
        if not doctor:
            print("Doctor not found.")
            return False

        # Unassign all patients linked to this doctor (set doctor_id to NULL)
        session.query(Patient).filter(Patient.doctor_id == doctor.doctor_id).update({"doctor_id": None})
        
        # Commit the patient update first
        session.commit()

        # Now, delete the doctor
        session.delete(doctor)
        session.commit()

        print(f"Doctor deleted: {doctor.first_name} {doctor.last_name} (All associated patients unlinked)")
        return True

    except Exception as e:
        session.rollback()
        print(f"Error deleting doctor: {e}")
        return False
    finally:
        session.close()