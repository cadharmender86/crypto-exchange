from pathlib import Path
from uuid import uuid4
import shutil

from fastapi import UploadFile

BASE_UPLOAD_DIR = Path("uploads/kyc")

ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "application/pdf",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


class StorageService:

    @staticmethod
    async def save_kyc_document(
        file: UploadFile,
        folder: str,
    ) -> tuple[str, int]:

        if file.content_type not in ALLOWED_MIME_TYPES:
            raise ValueError("Unsupported file type.")

        content = await file.read()

        if len(content) > MAX_FILE_SIZE:
            raise ValueError("File size exceeds 5 MB.")

        upload_dir = BASE_UPLOAD_DIR / folder
        upload_dir.mkdir(parents=True, exist_ok=True)

        extension = file.filename.split(".")[-1].lower()
        filename = f"{uuid4()}.{extension}"

        destination = upload_dir / filename
        
        with open(destination, "wb") as buffer:
            buffer.write(content)

        print(f"KYC file saved to: {destination.resolve()}")    

        return str(destination), len(content)