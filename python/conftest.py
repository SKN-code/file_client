import multiprocessing
import os
import time
import uuid
from argparse import Namespace

import pytest
import uvicorn
from fastapi.testclient import TestClient
from server import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client_test(app):
    # Technically we could use the same app for every test case,
    # but I feel it's better to have a separate app for each test
    return TestClient(app)


@pytest.fixture
def uuid_random():
    return str(uuid.uuid4())


@pytest.fixture
def file_name_random(uuid_random):
    path_relative = "./storage"
    path = os.path.join(os.path.dirname(__file__), path_relative)
    file_name = f"{path}/{uuid_random}.txt"

    return file_name, uuid_random


@pytest.fixture
def args():
    return Namespace(
        base_url="http://localhost:8080/",
        uuid="1234",
        backend="rest",
        output="output.txt",
    )


@pytest.fixture
def args_del():
    return Namespace(
        base_url="http://localhost:8080/",
        uuid="2345",
        backend="rest",
        output="output.txt",
    )


@pytest.fixture
def args_create():
    return Namespace(
        base_url="http://localhost:8080/",
        uuid="storage_test/test.txt",
        backend="rest",
        output="output.txt",
    )


@pytest.fixture(autouse=True)
def prepare_file(args):
    with open(f"storage/{args.uuid}.txt", "w") as f:
        f.write("test")
    yield
    os.remove(f"storage/{args.uuid}.txt")


@pytest.fixture(autouse=True, scope="session")
def serve_fastapi():
    app = create_app()

    def run_server():
        uvicorn.run(app, host="localhost", port=8080, log_level="info")

    process = multiprocessing.Process(target=run_server)
    process.start()
    time.sleep(0.1)  # wait for the server to start
    yield
    process.terminate()
