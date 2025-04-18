from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.routers.contacts import schemas
from db.database import get_db
from app.services.contacts.contact_service import ContactService
from app.services.user.user_service import UserService
from app.services.auth.jwt_manager import JWTManager
from app.dependencies.auth import jwt_manager
from db.models.user import User

router = APIRouter(
    prefix="/api/contacts",
    tags=["contacts"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=schemas.Contact, status_code=status.HTTP_201_CREATED)
def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_manager.get_current_user),
    contact_service: ContactService = Depends(ContactService),
):
    """
    Create a new contact for the current user.

    Args:
        contact (schemas.ContactCreate): The contact data to create.
        db (Session): The database session.
        current_user (User): The currently authenticated user.
        contact_service (ContactService): The contact service for interacting with the database.

    Returns:
        schemas.Contact: The created contact.
    """
    return contact_service.create_contact(
        db=db, contact_data=contact, user_id=current_user.id
    )


@router.get("/", response_model=List[schemas.Contact])
def read_contacts(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_manager.get_current_user),
    contact_service: ContactService = Depends(ContactService),
):
    """
    Retrieve a list of contacts for the current user.

    Args:
        skip (int): The number of records to skip (default: 0).
        limit (int): The maximum number of records to return (default: 10).
        db (Session): The database session.
        current_user (User): The currently authenticated user.
        contact_service (ContactService): The contact service for interacting with the database.

    Returns:
        List[schemas.Contact]: A list of contacts.
    """
    contacts = contact_service.get_contacts(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    return contacts


@router.get("/{contact_id}", response_model=schemas.Contact)
def read_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_manager.get_current_user),
    contact_service: ContactService = Depends(ContactService),
):
    """
    Retrieve a specific contact by ID for the current user.

    Args:
        contact_id (int): The ID of the contact to retrieve.
        db (Session): The database session.
        current_user (User): The currently authenticated user.
        contact_service (ContactService): The contact service for interacting with the database.

    Returns:
        schemas.Contact: The requested contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    db_contact = contact_service.get_contact(
        db, contact_id=contact_id, user_id=current_user.id
    )
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.put("/{contact_id}", response_model=schemas.Contact)
def update_contact(
    contact_id: int,
    contact: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_manager.get_current_user),
    contact_service: ContactService = Depends(ContactService),
):
    """
    Update a specific contact by ID for the current user.

    Args:
        contact_id (int): The ID of the contact to update.
        contact (schemas.ContactUpdate): The updated contact data.
        db (Session): The database session.
        current_user (User): The currently authenticated user.
        contact_service (ContactService): The contact service for interacting with the database.

    Returns:
        schemas.Contact: The updated contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    db_contact = contact_service.update_contact(
        db, contact_id=contact_id, contact_data=contact, user_id=current_user.id
    )
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.delete("/{contact_id}", response_model=schemas.Contact)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_manager.get_current_user),
    contact_service: ContactService = Depends(ContactService),
):
    """
    Delete a specific contact by ID for the current user.

    Args:
        contact_id (int): The ID of the contact to delete.
        db (Session): The database session.
        current_user (User): The currently authenticated user.
        contact_service (ContactService): The contact service for interacting with the database.

    Returns:
        schemas.Contact: The deleted contact.

    Raises:
        HTTPException: If the contact is not found.
    """
    db_contact = contact_service.delete_contact(
        db, contact_id=contact_id, user_id=current_user.id
    )
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact


@router.get("/search/", response_model=List[schemas.Contact])
def search_contacts(
    name: Optional[str] = None,
    lastname: Optional[str] = None,
    email: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_manager.get_current_user),
    contact_service: ContactService = Depends(ContactService),
):
    """
    Search for contacts by name, lastname, or email for the current user.

    Args:
        name (Optional[str]): The first name to search for.
        lastname (Optional[str]): The last name to search for.
        email (Optional[str]): The email to search for.
        db (Session): The database session.
        current_user (User): The currently authenticated user.
        contact_service (ContactService): The contact service for interacting with the database.

    Returns:
        List[schemas.Contact]: A list of matching contacts.
    """
    contacts = contact_service.get_contact_by_name_lastname_email(
        db, user_id=current_user.id, name=name, lastname=lastname, email=email
    )
    return contacts


@router.get("/birthdays/", response_model=List[schemas.Contact])
def contacts_with_upcoming_birthdays(
    db: Session = Depends(get_db),
    current_user: User = Depends(jwt_manager.get_current_user),
    contact_service: ContactService = Depends(ContactService),
):
    """
    Retrieve contacts with upcoming birthdays for the current user.

    Args:
        db (Session): The database session.
        current_user (User): The currently authenticated user.
        contact_service (ContactService): The contact service for interacting with the database.

    Returns:
        List[schemas.Contact]: A list of contacts with upcoming birthdays.
    """
    contacts = contact_service.get_contacts_with_upcoming_birthdays(
        db, user_id=current_user.id
    )
    return contacts
