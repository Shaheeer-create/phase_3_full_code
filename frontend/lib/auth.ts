/**
 * Better Auth client configuration
 *
 * CRITICAL: Uses JWT tokens signed with BETTER_AUTH_SECRET
 * The backend validates these tokens using the same secret.
 */
import { createAuthClient } from "better-auth/react";

export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || "http://localhost:3000",
});

/**
 * Get the current session
 */
export async function getSession() {
  try {
    const session = await authClient.getSession();
    return session;
  } catch (error) {
    console.error("Failed to get session:", error);
    return null;
  }
}

/**
 * Get the JWT access token for API requests
 * Reads from localStorage where AuthForm stores it after signup/login
 */
export async function getAccessToken(): Promise<string | null> {
  try {
    // Get token from localStorage (stored by AuthForm after signup/login)
    if (typeof window === "undefined") {
      return null;
    }

    const token = localStorage.getItem("auth_token");
    return token;
  } catch (error) {
    console.error("Failed to get access token:", error);
    return null;
  }
}
