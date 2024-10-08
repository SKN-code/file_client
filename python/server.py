import glob
import os
from datetime import datetime
from mimetypes import guess_extension, guess_type
from typing import Tuple, TypedDict
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request, Response, UploadFile


class StatResponseDict(TypedDict):
    create_datetime: str
    size: int
    mimetype: str
    name: str


def _abs_path(path_relative: str) -> str:
    return os.path.join(os.path.dirname(__file__), path_relative)


def get_type_mime(path: str) -> str:
    file_type, _ = guess_type(path)
    # If the file type is not recognized, it should be set to default unknown type
    return file_type if file_type else "application/octet-stream"


def _get_file_path(uuid: str) -> str:
    path = _abs_path("./storage")
    file_paths_all = glob.glob(f"{path}/{uuid}.*")
    if len(file_paths_all) != 1:
        # There is no other checking mechanism that would
        # prevent creating multiple files with the same name
        # to users not interacting trough the API
        raise HTTPException(status_code=500, detail="Multiple files found")

    return file_paths_all[0]


def _get_file(uuid: str) -> Tuple[str, str, bytes]:
    path = _get_file_path(uuid)

    with open(path, "rb") as f:
        file_content = f.read()
    file_name = path.split("/")[-1]
    file_type = get_type_mime(path)

    return file_name, file_type, file_content


def get_file_meta(uuid: str) -> Tuple[str, str, int, str]:
    path = _get_file_path(uuid)

    file_name = path.split("/")[-1]
    file_type = get_type_mime(path)
    file_size = os.path.getsize(path)

    file_creation_time = os.path.getctime(path)
    creation_datetime = datetime.fromtimestamp(file_creation_time).isoformat()

    return file_name, file_type, file_size, creation_datetime


def check_if_file_exists(uuid: str, path_relative: str = "./storage") -> bool:
    path = _abs_path(path_relative)
    # It is expected that files will be in format of uuid.extension
    file_names = [file.split(".")[0] for file in os.listdir(path)]
    return uuid in file_names


def create_app() -> FastAPI:
    app = FastAPI()

    @app.middleware("http")
    async def add_logging_header(request: Request, call_next):
        print(request.url)
        response = await call_next(request)
        return response

    @app.post("/file/create")
    def file_create(file: UploadFile) -> str:
        if not file.filename:
            raise HTTPException(status_code=400, detail="Invalid file content type")

        file_extension = file.filename.split(".")[-1]
        file_name = str(uuid4())
        path = _abs_path("./storage")
        with open(f"{path}/{file_name}.{file_extension}", "wb") as f:
            f.write(file.file.read())

        print(f"File {file_name}{file_extension} created")
        return file_name

    @app.get("/file/{uuid}/stat")
    def file_stat(uuid: str) -> StatResponseDict:
        if not check_if_file_exists(uuid):
            raise HTTPException(status_code=404, detail="File not found")

        file_name, file_type, file_size, creation_datetime = get_file_meta(uuid)
        return {
            "create_datetime": creation_datetime,
            "size": file_size,
            "mimetype": file_type,
            "name": file_name,
        }

    @app.get("/file/{uuid}/read")
    def file_read(response: Response, uuid: str) -> Response:
        if not check_if_file_exists(uuid):
            raise HTTPException(status_code=404, detail="File not found")

        file_name, file_type, file_content = _get_file(uuid)

        response.headers["Content-Disposition"] = file_name
        response.headers["Content-Type"] = file_type
        response.body = file_content
        response.status_code = 200

        return response

    @app.post("/file/{uuid}/update")
    def file_write(uuid: str):
        raise HTTPException(
            status_code=418,
            detail="Method not needed for scope of this execise",
        )

    @app.delete("/file/{uuid}/delete")
    def file_delete(uuid: str) -> str:
        if not check_if_file_exists(uuid):
            print(f"File {uuid} not found")
            raise HTTPException(status_code=404, detail="File not found")

        path = _abs_path("./storage")
        for file_name in glob.glob(f"{path}/{uuid}.*"):
            os.remove(file_name)
        return uuid

    return app
