from pathlib import Path
from typing import BinaryIO
from PIL import Image


class StorageError(Exception):
    """Base exception for storage failures."""


class ImageNotFoundError(StorageError):
    """Raised when expected image does not exist."""


class InvalidImageError(StorageError):
    """Raised when uploaded content is not a valid image."""


class StorageRepository:
    def __init__(self, uploads_root: str = "uploads", analysis_root: str = "analysis_artifacts") -> None:
        self.uploads_root = Path(uploads_root)
        self.analysis_root = Path(analysis_root)
        self.uploads_root.mkdir(parents=True, exist_ok=True)
        self.analysis_root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def validate_image(file_obj: BinaryIO) -> None:
        try:
            Image.open(file_obj).verify()
            file_obj.seek(0)
        except Exception as exc:
            raise InvalidImageError("Invalid image file") from exc

    def save_upload(self, file_obj: BinaryIO, request_id: str) -> Path:
        request_dir = self.uploads_root / request_id
        request_dir.mkdir(parents=True, exist_ok=True)
        image_path = request_dir / "original.png"
        try:
            image = Image.open(file_obj)
            image.save(image_path)
            return image_path
        except Exception as exc:
            raise StorageError(f"File save failed: {exc}") from exc

    def get_uploaded_image(self, request_id: str) -> Path:
        image_path = self.uploads_root / request_id / "original.png"
        if not image_path.exists():
            raise ImageNotFoundError("Image not found")
        return image_path

    def create_analysis_dir(self, request_id: str) -> Path:
        analysis_dir = self.analysis_root / request_id
        analysis_dir.mkdir(parents=True, exist_ok=True)
        return analysis_dir
