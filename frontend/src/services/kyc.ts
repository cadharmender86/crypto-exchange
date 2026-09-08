import { apiFetch, getAccessToken } from "@/lib/api";
import type {
  PersonalInfo,
  PersonalInfoRequest,
  KYCUploadResponse,
} from "@/types/kyc";

export async function getKYCProfile(): Promise<PersonalInfo> {
  const token = getAccessToken();

  if (!token) {
    throw new Error("Not authenticated");
  }

  return apiFetch<PersonalInfo>(
    "/kyc/profile",
    {},
    token
  );
}

export async function savePersonalInfo(
  payload: PersonalInfoRequest
): Promise<PersonalInfo> {
  const token = getAccessToken();

  if (!token) {
    throw new Error("Not authenticated");
  }

  return apiFetch<PersonalInfo>(
    "/kyc/personal-info",
    {
      method: "PUT",
      body: JSON.stringify(payload),
    },
    token
  );
}

export async function uploadKYCDocument(
  documentType:
    | "pan"
    | "aadhaar-front"
    | "aadhaar-back"
    | "selfie",
  file: File
) {
  const token = getAccessToken();

  if (!token) throw new Error("Not authenticated");

  const form = new FormData();
  form.append("file", file);

  return apiFetch<KYCUploadResponse>(
    `/kyc/upload/${documentType}`,
    {
      method: "POST",
      body: form,
      headers: {},
    },
    token
  );
}