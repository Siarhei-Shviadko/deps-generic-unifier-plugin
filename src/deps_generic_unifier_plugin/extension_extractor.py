from pathlib import Path


class ExtensionExtractor:
    def __init__(self, path: str):
        self._path: Path = Path(path)

    def extract(self) -> str:
        extension = self._path.suffix
        extension = extension.strip(".")

        return extension.lower()
