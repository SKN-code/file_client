import os
from typing import Tuple

import pytest
import server
from fastapi.testclient import TestClient


def test_file_exists(file_name_random: Tuple[str, str]):
    file_name, uuid = file_name_random
    open(file_name, "a")

    assert server.check_if_file_exists(
        uuid
    ), f"This file ({file_name}.txt) should exist"

    os.remove(file_name)

    assert not server.check_if_file_exists(
        uuid
    ), f"This file ({file_name}.txt) should not exist"


# TEST REST enpoints
def test_create(client_test: TestClient):
    path_relative = "./storage_test/test.txt"
    path = os.path.join(os.path.dirname(__file__), path_relative)
    with open(path, "rb") as f:
        response = client_test.post(url="/file/create", files={"file": f})
    try:
        assert response.status_code == 200
    finally:
        file_name = response.content.decode().strip('"')
        os.remove(
            os.path.join(os.path.dirname(__file__), "./storage", f"{file_name}.txt")
        )


def test_read(client_test: TestClient, file_name_random: Tuple[str, str]):
    file_name, uuid = file_name_random
    with open(file_name, "a") as f:
        f.write("Hello World")

    try:
        response = client_test.get(url=f"/file/{uuid}/read")
        assert response.status_code == 200
        assert response.content.decode().strip('"') == "Hello World"
        assert response.headers["Content-Type"] == "text/plain"
        assert response.headers["Content-Disposition"] == f"{uuid}.txt"
    finally:
        os.remove(file_name)


def test_stat(client_test: TestClient, file_name_random: Tuple[str, str]):
    file_name, uuid = file_name_random
    with open(file_name, "a") as f:
        f.write("Hello World")

    try:
        response = client_test.get(url=f"/file/{uuid}/stat")
        file_name_, file_type, file_size, creation_datetime = server.get_file_meta(uuid)
        assert response.status_code == 200
        assert response.json() == {
            "create_datetime": creation_datetime,
            "size": file_size,
            "mimetype": file_type,
            "name": file_name_,
        }
    finally:
        os.remove(file_name)


def test_update(client_test: TestClient, uuid_random: str):
    response = client_test.post(url=f"/file/{uuid_random}/update")
    assert response.status_code == 418 and response.json() == {
        "detail": "Method not needed for scope of this execise"
    }


def test_delete(client_test: TestClient, file_name_random: Tuple[str, str]):
    file_name, uuid = file_name_random
    open(file_name, "a")

    response = client_test.delete(url=f"/file/{uuid}/delete")
    file_name_returned = response.content.decode().strip('"')
    assert response.status_code == 200 and file_name_returned == uuid
