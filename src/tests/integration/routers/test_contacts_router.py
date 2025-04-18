from unittest.mock import patch
from conftest import test_user


def test_create_contact(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "birthday": "1990-01-01",
    }

    response = client.post("/api/contacts/", headers=headers, json=contact_data)

    assert response.status_code == 201, response.text

    data = response.json()
    assert data["first_name"] == contact_data["first_name"]
    assert data["last_name"] == contact_data["last_name"]
    assert data["birthday"] == contact_data["birthday"]


def test_read_contacts(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/contacts/", headers=headers)

    assert response.status_code == 200, response.text

    data = response.json()
    assert isinstance(data, list)


def test_read_contact(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create a contact first
    contact_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "birthday": "1985-05-15",
    }
    create_response = client.post("/api/contacts/", headers=headers, json=contact_data)
    assert create_response.status_code == 201, create_response.text
    created_contact = create_response.json()

    # Retrieve the created contact
    contact_id = created_contact["id"]
    response = client.get(f"/api/contacts/{contact_id}", headers=headers)

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == contact_id
    assert data["first_name"] == contact_data["first_name"]
    assert data["last_name"] == contact_data["last_name"]


def test_update_contact(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create a contact first
    contact_data = {
        "first_name": "Alice",
        "last_name": "Brown",
        "birthday": "1992-03-10",
    }
    create_response = client.post("/api/contacts/", headers=headers, json=contact_data)
    assert create_response.status_code == 201, create_response.text
    created_contact = create_response.json()

    # Update the created contact
    contact_id = created_contact["id"]
    updated_data = {
        "first_name": "Alice Updated",
        "last_name": "Brown Updated",
        "birthday": "1992-03-11",
    }
    response = client.put(
        f"/api/contacts/{contact_id}", headers=headers, json=updated_data
    )

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == contact_id
    assert data["first_name"] == updated_data["first_name"]
    assert data["last_name"] == updated_data["last_name"]
    assert data["birthday"] == updated_data["birthday"]


def test_delete_contact(client, get_token):
    token = get_token
    headers = {"Authorization": f"Bearer {token}"}

    # Create a contact first
    contact_data = {
        "first_name": "Bob",
        "last_name": "Green",
        "birthday": "1980-07-20",
    }
    create_response = client.post("/api/contacts/", headers=headers, json=contact_data)
    assert create_response.status_code == 201, create_response.text
    created_contact = create_response.json()

    # Delete the created contact
    contact_id = created_contact["id"]
    response = client.delete(f"/api/contacts/{contact_id}", headers=headers)

    assert response.status_code == 200, response.text

    data = response.json()
    assert data["id"] == contact_id
    assert data["first_name"] == contact_data["first_name"]
    assert data["last_name"] == contact_data["last_name"]
