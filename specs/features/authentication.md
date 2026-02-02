# Feature: User Authentication

## User Stories
- As a user, I can sign up with email and password
- As a user, I can log in with email and password
- As a user, I can log out
- As a user, I can see my email in the UI when logged in
- As a user, I am redirected to login if I try to access tasks unauthenticated

## Acceptance Criteria

### Sign Up
**Given** new user with email "user@example.com"
**When** they sign up with password (min 8 chars)
**Then** account is created in Better Auth
**And** they are automatically logged in
**And** JWT token is stored
**And** they are redirected to /tasks

### Login
**Given** existing user
**When** they enter correct credentials
**Then** JWT token is issued
**And** stored in frontend
**And** they see their tasks

### Logout
**When** user clicks logout
**Then** JWT token is cleared
**And** they are redirected to login page

### Protected Routes
**Given** unauthenticated user
**When** they try to access /tasks
**Then** they are redirected to /login

## Technical Requirements
- Better Auth configured with JWT plugin enabled
- JWT secret shared between frontend and backend
- Token expiry: 7 days
- Password requirements: min 8 characters, 1 number
- Email validation required
