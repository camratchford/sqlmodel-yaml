import subprocess
from pathlib import Path


this_directory = Path(__file__).parent
project_root = this_directory.parent.parent


def run(cmd, check=True):
    print(f"Running: {cmd}")
    subprocess.run(cmd, shell=True, check=check, cwd=project_root)


def cli():
    if not project_root.joinpath("tests").exists():
        raise ValueError(
            "The tests directory is not available. "
            "Did forget to install this pacakge with 'pip install -e'?"
        )
    run("pytest ./tests")


if __name__ == "__main__":
    cli()
