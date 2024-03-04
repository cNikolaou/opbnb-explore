import csv
from pathlib import Path


def to_relative_path(file_path: Path, base_dir: Path) -> Path:
    """
    Helper function to return the relative path of `file_path` with
    respect to `base_dir`
    """

    relative_path = file_path.relative_to(base_dir)
    return relative_path


def remove_file_and_parent_dirs(path: Path):

    parent_dir, parent_of_parent_dir = path.parent, path.parent.parent

    # remove all items from parent dir and remove the parent dir
    for fl in parent_dir.iterdir():
        fl.unlink()
    parent_dir.rmdir()

    # remove all items from parent of parent dir and remove the parent dir
    for fl in parent_of_parent_dir.iterdir():
        fl.unlink()
    parent_of_parent_dir.rmdir()


def change_dir(dir: Path, replacements: dict) -> Path:
    """
    Replace the parts of Path `dir` based on the replacements to generate
    a new Path that is returned by the function
    """

    path_parts = list(dir.parts)
    new_path_parts = [replacements.get(part, part) for part in path_parts]
    new_path = Path(*new_path_parts)
    return new_path


def csv_has_row_data(file_path: Path):

    try:
        with open(file_path, "r") as csv_file:
            reader = csv.reader(csv_file)
            # skip header
            next(reader)
            return any(reader)
    except StopIteration:
        return False
