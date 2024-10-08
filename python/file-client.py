import argparse

from file_utils import CHOICES_BACKEND, create, delete, read, stat

SUBCOMMANDS = {
    "create": create,
    "stat": stat,
    "read": read,
    "delete": delete,
}

if __name__ == "__main__":
    choices_command = SUBCOMMANDS.keys()

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        prog="file-client",
        usage="""
            file-client [options] create filename
            file-client [options] read UUID
            file-client [options] stat UUID
            file-client [options] delete UUID
            file-client --help
            """,
        epilog="Made by Petr Vorlíček",
    )
    parser.add_argument(
        "--backend",
        type=str,
        choices=CHOICES_BACKEND,
        metavar="BACKEND",
        default="grpc",
        help="Set a backend to be used, choices are grpc and rest. Default is grpc.",
    )
    parser.add_argument(
        "--grpc-server",
        type=str,
        default="localhost:50051",
        help="Set a host and port of the gRPC server. Default is localhost:50051.",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost/",
        help="Set a base URL for a REST server. Default is http://localhost/.",
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Set the file where to store the output. Default is -, i.e. the stdout.",
    )
    parser.add_argument(
        "command",
        type=str,
        choices=choices_command,
        metavar=" | ".join(choices_command),
        help="Creates the resoure. | Prints the file metadata in a human-readable manner. | Outputs the file content. | Deletes the resource.",
    )
    parser.add_argument(
        "uuid",
        type=str,
        help="File path to upload. | UUID of the file to be processed.",
        metavar="filename | UUID",
    )

    args = parser.parse_args()
    SUBCOMMANDS[args.command](args)
