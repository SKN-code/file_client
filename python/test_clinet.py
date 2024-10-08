import os
from unittest.mock import mock_open, patch
from datetime import datetime
import requests
from file_utils import create, delete, read, stat
from server import get_type_mime


def test_read(args):
    try:
        read(args)
        with open(args.output, "r") as f:
            assert f.read() == "test"
    finally:
        os.remove(args.output)


def test_stat(args):
    try:
        stat(args)
        path = f"storage/{args.uuid}.txt"
        file_name = path.split("/")[-1]
        file_type = get_type_mime(file_name)
        file_size = os.path.getsize(path)

        file_creation_time = os.path.getctime(path)
        creation_datetime = datetime.fromtimestamp(file_creation_time).isoformat()

        with open(args.output) as f:
            result = f.read()
        assert f"Creation datetime: {creation_datetime}" in result
        assert f"size: {file_size}" in result
        assert f"mimetype: {file_type}" in result
        assert f"name: {file_name}" in result
    finally:
        os.remove(args.output)


def test_delete(args_del):
    try:
        open(f"storage/{args_del.uuid}.txt", "a")
        delete(args_del)
        with open(args_del.output) as f:
            result = f.read()
        assert result == args_del.uuid
        assert f"{args_del.uuid}.txt" not in os.listdir("storage")
    finally:
        os.remove(args_del.output)


def test_create(args_create):
    try:
        create(args_create)
        with open(args_create.output) as f:
            result = f.read()
        assert f"{result}.txt" in os.listdir("storage")

        with open(f"storage/{result}.txt") as f:
            assert f.read() == "test"
    finally:
        os.remove(args_create.output)
        os.remove(f"storage/{result}.txt")
