export interface PersonalInfo {
  kyc_status: string;

  first_name: string;
  last_name: string;

  date_of_birth: string;

  nationality: string;
  country: string;
  state: string;
  city: string;

  address_line1: string;
  address_line2: string;
  postal_code: string;
}

export interface PersonalInfoRequest {
  first_name: string;
  last_name: string;

  date_of_birth: string;

  nationality: string;
  country: string;
  state: string;
  city: string;

  address_line1: string;
  address_line2: string;
  postal_code: string;
}

export type KYCDocument = {
  id: string;
  document_type: "PAN" | "AADHAAR_FRONT" | "AADHAAR_BACK" | "SELFIE";
  status: "PENDING" | "VERIFIED" | "REJECTED";
  file_name: string;
  uploaded_at: string;
  verified_at?: string | null;
  rejection_reason?: string | null;
};

export type KYCUploadResponse = {
  message: string;
  document: KYCDocument;
};