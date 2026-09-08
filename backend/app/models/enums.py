from enum import Enum


class KYCStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    DRAFT = "DRAFT"
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class DocumentType(str, Enum):
    PAN = "PAN"
    AADHAAR_FRONT = "AADHAAR_FRONT"
    AADHAAR_BACK = "AADHAAR_BACK"
    PASSPORT = "PASSPORT"
    DRIVING_LICENSE = "DRIVING_LICENSE"
    SELFIE = "SELFIE"


class DocumentStatus(str, Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"