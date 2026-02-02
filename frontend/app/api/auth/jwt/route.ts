import { auth } from "@/lib/auth-server";
import { NextRequest, NextResponse } from "next/server";
import jwt from "jsonwebtoken";

export const runtime = "nodejs";

/**
 * GET /api/auth/jwt
 *
 * Converts Better Auth session into a JWT token for backend API calls.
 *
 * Flow:
 * 1. Client authenticates with Better Auth (gets session cookie)
 * 2. Client calls this endpoint to get JWT token
 * 3. Client uses JWT token for backend API requests
 */
export async function GET(request: NextRequest) {
  try {
    // Get session token from cookie
    const sessionToken = request.cookies.get("better-auth.session_token")?.value;

    if (!sessionToken) {
      return NextResponse.json(
        { error: "Unauthorized - No session" },
        { status: 401 }
      );
    }

    // Verify session exists in database
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session?.user?.id) {
      return NextResponse.json(
        { error: "Unauthorized - Invalid session" },
        { status: 401 }
      );
    }

    // Generate JWT token with user_id in 'sub' claim
    const token = jwt.sign(
      {
        sub: session.user.id, // user_id in 'sub' claim (backend expects this)
        email: session.user.email,
        name: session.user.name,
      },
      process.env.BETTER_AUTH_SECRET!,
      {
        algorithm: "HS256",
        expiresIn: "7d",
      }
    );

    return NextResponse.json({
      token,
      expiresIn: "7d",
    });
  } catch (error) {
    console.error("Failed to generate JWT:", error);
    return NextResponse.json(
      { error: "Failed to generate token" },
      { status: 500 }
    );
  }
}
