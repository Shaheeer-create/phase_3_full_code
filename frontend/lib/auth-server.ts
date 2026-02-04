import { betterAuth } from "better-auth";
import { jwt } from "better-auth/plugins";
import { Pool } from "pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: { rejectUnauthorized: false },
});

export const auth = betterAuth({
  database: pool,

  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
    minPasswordLength: 8,
  },

  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24,
  },

  plugins: [
    jwt({
      jwt: {
        expirationTime: "7d",
      },
    }),
  ],

  baseURL: process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : (process.env.BETTER_AUTH_URL || "http://localhost:3000"),
  secret: process.env.BETTER_AUTH_SECRET || "fallback-secret-for-development",
});
