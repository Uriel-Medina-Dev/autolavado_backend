import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_crear_usuario_exitoso():
	payload = {
		"rol_Id": 1,
		"user_name": "Test",
		"user_1lastname": "Uno",
		"user_2lastname": "Dos",
		"user": "testuser",
		"user_password": "secret123",
		"user_address": "Calle 123",
		"user_phone": "1234567890",
		"status": True,
		"creation_date": "2026-02-25T00:00:00",
		"modification_date": "2026-02-25T00:00:00"
	}

	response = client.post("/users/", json=payload)
	assert response.status_code in (200, 201)

	data = response.json()
	assert data.get("user") == payload["user"]
	assert data.get("user_name") == payload["user_name"]


def test_crear_usuario_datos_invalidos():
	# Payload missing required fields (e.g., user_password)
	invalid_payload = {
		"rol_Id": 1,
		"user_name": "test1",
		"user_1lastname": "Uno",
		"user_2lastname": "Dos",
		"user": "baduser",
		"user_address": "Calle 123",
		"user_phone": "1234567890",
		"status": True,
		"creation_date": "2026-02-25T00:00:00",
		"modification_date": "2026-02-25T00:00:00"
	}

	response = client.post("/users/", json=invalid_payload)
	# FastAPI should return 422 Unprocessable Entity for validation errors
	assert response.status_code == 422