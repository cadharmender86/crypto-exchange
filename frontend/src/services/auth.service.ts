import { apiClient } from "./apiClient";

export interface RegisterRequest {
  first_name: string;
  last_name: string;
  email: string;
  mobile: string;
  password: string;
  referral_code?: string;
}

export interface RegisterResponse {
  user_id: string;
  email: string;
  email_verified: boolean;
  kyc_status: string;
  message: string;
}

export function registerUser(payload: RegisterRequest) {
  return apiClient<RegisterResponse>("/auth/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// For Login Request

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export async function loginUser(
  payload: LoginRequest
): Promise<LoginResponse> {
  return apiClient<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}