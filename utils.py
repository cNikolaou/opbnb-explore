from pathlib import Path


def to_relative_path(file_path: Path, base_dir: Path) -> Path:
    """
    Helper function to return the relative path of `file_path` with
    respect to `base_dir`
    """

    relative_path = file_path.relative_to(base_dir)
    return relative_path
