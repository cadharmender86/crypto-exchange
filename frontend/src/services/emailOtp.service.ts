import { apiClient } from "./apiClient";

export interface VerifyEmailRequest {
  email: string;
  otp: string;
}

export interface ResendEmailOtpRequest {
  email: string;
}

export interface MessageResponse {
  message: string;
}

export function verifyEmail(payload: VerifyEmailRequest) {
  return apiClient<MessageResponse>("/auth/verify-email", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function resendEmailOtp(payload: ResendEmailOtpRequest) {
  return apiClient<MessageResponse>("/auth/resend-email-otp", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}