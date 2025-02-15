from sqlalchemy.orm import Session
from database import SessionLocal
from models import Patient, Doctor

def create_patient(first_name: str, last_name: str, email: str, password: str, doctor_id: int = None):
    """
    Creates a new patient and adds them to the database.

    :param first_name: Patient's first name
    :param last_name: Patient's last name
    :param email: Patient's email (must be unique)
    :param password: Password (should be hashed before storage)
    :param doctor_id: (Optional) ID of the doctor assigned to this patient
    :return: The created patient object or None if an error occurs
    """
    session = SessionLocal()

    try:
        existing_patient = session.query(Patient).filter(Patient.email == email).first()
        if existing_patient:
            print("A patient with this email already exists.")
            return None
        
        if doctor_id:
            doctor = session.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
            if not doctor:
                print("Doctor ID does not exist.")
                return None


        new_patient = Patient(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,  # TODO: Hash password before storage
            doctor_id=doctor_id
        )

        session.add(new_patient)
        session.commit()
        session.refresh(new_patient)

        print(f"Patient created: {new_patient.first_name} {new_patient.last_name} ({new_patient.email})")
        return new_patient

    except Exception as e:
        session.rollback()
        print(f"Error while adding the patient: {e}")
        return None

    finally:
        session.close()

def get_patient_by_email(email: str):
    """
    Retrieves a patient from the database using their email.

    :param email: The email of the patient to retrieve
    :return: The Patient object if found, else None
    """
    session = SessionLocal()
    try:
        patient = session.query(Patient).filter(Patient.email == email).first()
        return patient
    except Exception as e:
        print(f"Error retrieving patient: {e}")
        return None
    finally:
        session.close()


def update_patient(email: str, first_name: str = None, last_name: str = None, doctor_id: int = None):
    """
    Updates patient details in the database.

    :param email: The email of the patient to update
    :param first_name: (Optional) New first name
    :param last_name: (Optional) New last name
    :param password: (Optional) New password (should be hashed before storage)
    :return: The updated patient object or None if not found
    """
    session = SessionLocal()
    try:
        patient = session.query(Patient).filter(Patient.email == email).first()
        if not patient:
            print("Patient not found.")
            return None

        # Update fields if new values are provided
        if first_name:
            patient.first_name = first_name
        if last_name:
            patient.last_name = last_name

        # Update doctor assignment if doctor_id is provided
        if doctor_id is not None:
            doctor = session.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
            if not doctor:
                print("Doctor ID does not exist.")
                return None
            patient.doctor_id = doctor_id

        session.commit()
        session.refresh(patient)

        print(f"Patient updated: {patient.first_name} {patient.last_name}")
        return patient

    except Exception as e:
        session.rollback()
        print(f"Error updating patient: {e}")
        return None
    finally:
        session.close()


def delete_patient(email: str):
    """
    Deletes a patient from the database.

    :param email: The email of the patient to delete
    :return: True if deleted successfully, False otherwise
    """
    session = SessionLocal()
    try:
        patient = session.query(Patient).filter(Patient.email == email).first()
        if not patient:
            print("Patient not found.")
            return False

        session.delete(patient)
        session.commit()

        print(f"Patient deleted: {patient.first_name} {patient.last_name}")
        return True

    except Exception as e:
        session.rollback()
        print(f"Error deleting patient: {e}")
        return False
    finally:
        session.close()