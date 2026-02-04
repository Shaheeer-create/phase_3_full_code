# TodoAI Frontend Deployment Guide

## Application Overview
TodoAI is a Next.js-based task management application with AI-powered assistance. It features:
- User authentication system
- Task management with CRUD operations
- AI-powered chat functionality
- Responsive design with dark/light themes

## Backend API Configuration
The frontend connects to a backend API for data persistence and AI services.

### Backend API URLs
```
Current: https://shaheernaeem25-phase-3-backend.hf.space
Previous: https://shaheernaeem25-todo-task2.hf.space/
```

## Environment Variables Required

### Production Environment Variables
The following environment variables need to be set in your Vercel project:

1. **NEXT_PUBLIC_API_URL** (Required)
   - Value: `https://shaheernaeem25-phase-3-backend.hf.space`
   - Purpose: Points the frontend to the backend API for tasks, chat, and user data

2. **BETTER_AUTH_SECRET** (Required)
   - Value: A secure secret key (minimum 32 characters)
   - Purpose: Used for signing authentication tokens
   - Example: `8iKl8dG1yzILJufxsyJDvB7v+2Osyo07cKusfZvDfvU=`

3. **NEXT_PUBLIC_API_BASE_URL** (Previously Set)
   - Value: `https://shaheernaeem25-todo-task2.hf.space/`
   - Purpose: Alternative API base URL that was previously configured

4. **VERCEL_OIDC_TOKEN** (Development/Build Token)
   - Purpose: Vercel OIDC token for authentication during build process
   - Note: This is automatically managed by Vercel

## Deployment Process

### Prerequisites
- Vercel CLI installed (`npm i -g vercel`)
- Logged into your Vercel account (`vercel login`)

### Step-by-Step Deployment

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Set Environment Variables in Vercel**
   ```bash
   # Set the backend API URL
   echo 'https://shaheernaeem25-phase-3-backend.hf.space' | vercel env add NEXT_PUBLIC_API_URL production

   # Set the auth secret (generate your own secure secret)
   echo 'your-secure-secret-key-here' | vercel env add BETTER_AUTH_SECRET production
   ```

3. **Deploy to Production**
   ```bash
   vercel --prod --yes
   ```

4. **Access Your Deployed Application**
   - Vercel will provide a unique URL for your deployment
   - Example: `https://frontend-xyz123abc-your-project.vercel.app`

## Previously Configured Environment Values

The following values were previously stored in your environment:

```
NEXT_PUBLIC_API_BASE_URL="https://shaheernaeem25-todo-task2.hf.space/"
VERCEL_OIDC_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Im1yay00MzAyZWMxYjY3MGY0OGE5OGFkNjFkYWRlNGEyM2JlNyJ9.eyJpc3MiOiJodHRwczovL29pZGMudmVyY2VsLmNvbS9zaGFoZWVycy1wcm9qZWN0cy02N2UxY2NmMiIsInN1YiI6Im93bmVyOnNoYWhlZXJzLXByb2plY3RzLTY3ZTFjY2YyOnByb2plY3Q6ZnJvbnRlbmQ6ZW52aXJvbm1lbnQ6ZGV2ZWxvcG1lbnQiLCJzY29wZSI6Im93bmVyOnNoYWhlZXJzLXByb2plY3RzLTY3ZTFjY2YyOnByb2plY3Q6ZnJvbnRlbmQ6ZW52aXJvbm1lbnQ6ZGV2ZWxvcG1lbnQiLCJhdWQiOiJodHRwczovL3ZlcmNlbC5jb20vc2hhaGVlcnMtcHJvamVjdHMtNjdlMWNjZjIiLCJvd25lciI6InNoYWhlZXJzLXByb2plY3RzLTY3ZTFjY2YyIiwib3duZXJfaWQiOiJ0ZWFtX202SGxQNnNuWDJ1MWVUYU01UXpjMHNJSSIsInByb2plY3QiOiJmcm9udGVuZCIsInByb2plY3RfaWQiOiJwcmpfZGc5d1V1TmZMMHRFNU85Zjg2SFlaUkROMThTRyIsImVudmlyb25tZW50IjoiZGV2ZWxvcG1lbnQiLCJwbGFuIjoiaG9iYnkiLCJ1c2VyX2lkIjoiQUdJZWc4QzRJYTZnMUxzdHFnbXdtU1pHIiwibmJmIjoxNzcwMTAwMTYzLCJpYXQiOjE3NzAxMDAxNjMsImV4cCI6MTc3MDE0MzM2M30.KD41BUgw5lMOoUnoUey_4-Dk_97RTfAghnQdDW8QrWV15nITW2PtfWVXQrLZji_cIeJ2fYfGs3fQjK9wVT4umEQpGkqC_ZsqPFhF1h1YFLBb76r1YSxBCYJ1LyknaaqjdO0V8GkkHJmCA0A8FKHqO4b72BIYmLO40Lrc90LDfxkJ43QcUlxdoC7EnDKEiClFiKKktpLoC8DLziDtnjjPtjvvUcJ7QOzl6wMbGsm8BW_r3e0c_iWbNos0ZLivpIgmzqJMBBTXsrry3DlP8GmjZSx8spiSz0b1-BRENdLzd69OSnDbBSPSNiQRMA5q7E2faD8iVQDAhH3lAun3E2MUuw"
```

## Troubleshooting Common Issues

### Issue: 401 Unauthorized Error
**Cause**: Vercel deployment protection is enabled
**Solution**:
- Access the Vercel dashboard
- Navigate to your project settings
- Disable "Deployment Protection" or "Password Protection"
- Or access the site while logged into your Vercel account

### Issue: API Connection Errors
**Cause**: Incorrect NEXT_PUBLIC_API_URL
**Solution**: Verify the backend API URL is correctly set in environment variables

### Issue: Authentication Problems
**Cause**: Invalid BETTER_AUTH_SECRET
**Solution**: Ensure the secret is at least 32 characters and properly set

## Application Architecture

### Frontend Components
- Next.js 16.1.6 with App Router
- React 19 with TypeScript
- Tailwind CSS for styling
- Better Auth for authentication
- PostgreSQL database connection

### API Integration
- Tasks API: `/api/tasks`
- Chat API: `/api/conversations`
- Authentication API: `/api/auth`

### Key Pages
- `/` - Homepage (redirects to tasks)
- `/tasks` - Task management dashboard
- `/chat` - AI-powered chat interface
- `/login` - User login page
- `/signup` - User registration page

## Post-Deployment Steps

1. **Test Authentication Flow**
   - Visit `/signup` to create an account
   - Verify login functionality at `/login`
   - Test task creation and management at `/tasks`

2. **Verify API Connectivity**
   - Ensure tasks can be created, updated, and deleted
   - Test the chat functionality with the AI assistant

3. **Custom Domain (Optional)**
   - Add your custom domain in Vercel project settings
   - Update DNS records as instructed by Vercel

## Security Notes

- Keep your BETTER_AUTH_SECRET secure and do not expose it in client-side code
- The application uses JWT tokens for API authentication
- All API requests include proper authorization headers
- Passwords are securely hashed using Argon2 algorithm