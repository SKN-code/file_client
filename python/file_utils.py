from argparse import Namespace
from mimetypes import guess_type

import requests

CHOICES_BACKEND = ["grpc", "rest"]


def handle_grpc(func):
    def handler_inner(args: Namespace):
        if args.backend == "grpc":
            raise NotImplementedError("gRPC is not implemented")
        return func(args)

    return handler_inner


def handle_write(func):
    def handler_inner(args: Namespace):
        if args.output:
            with open(args.output, "w") as f:
                f.write(func(args))
        else:
            print(func(args))

    return handler_inner


@handle_grpc
@handle_write
def stat(args: Namespace):
    response = requests.get(f"{args.base_url}file/{args.uuid}/stat")
    return """
    Creation datetime: {create_datetime}
    size: {size}
    mimetype: {mimetype}
    name: {name}
    """.format(
        **response.json()
    )


@handle_grpc
def read(args: Namespace):
    content = requests.get(f"{args.base_url}file/{args.uuid}/read").content

    if args.output:
        with open(args.output, "wb") as f:
            f.write(content)
    else:
        print(content.decode())


@handle_grpc
@handle_write
def delete(args: Namespace):
    response = requests.delete(f"{args.base_url}file/{args.uuid}/delete")
    return response.json()


@handle_grpc
@handle_write
def create(args: Namespace):
    with open(args.uuid, "rb") as f:
        response = requests.post(f"{args.base_url}file/create", files={"file": f})
    return response.json()
