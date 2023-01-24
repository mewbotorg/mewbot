import os
import pathlib
import sys

import pip


def install(path: pathlib.Path) -> None:
    pip.main(["install", "--editable", str(path) + "/"])


def main() -> bool:
    dot = pathlib.Path()

    if not (dot/"setup.py").exists():
        print("Unable to find setup.py in current folder")
        print("This script expects to be run from the root of the mewbot repo")
        return False

    install(dot)

    for path, _, files in os.walk(dot/"plugins"):
        if "setup.py" in files:
            install(path)


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
