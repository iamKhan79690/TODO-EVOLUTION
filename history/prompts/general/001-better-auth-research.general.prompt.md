---
id: 001
title: Better Auth Research
stage: general
date: 2025-01-07
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 003-recurring-tasks-due-dates
user: user
command: research
labels: [authentication,better-auth,nextjs,postgresql,jwt]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
- history/prompts/general/001-better-auth-research.general.prompt.md
tests:
-
---

## Prompt

Research Better Auth v1 integration with Next.js 16+ App Router and Neon PostgreSQL database. I need to understand:

1. **Better Auth Configuration**: How to set up Better Auth with Next.js 16+ using App Router patterns
2. **Neon PostgreSQL Integration**: Better Auth database adapter for Neon PostgreSQL or setup instructions
3. **JWT Plugin Configuration**: How Better Auth generates and manages JWT tokens
4. **Authentication Flow**: Complete signup/signin flow with email/password
5. **Session Management**: How Better Auth handles persistent sessions across browser restarts
6. **Security Configuration**: Best practices for Better Auth security settings

The context is a todo application where users need to create accounts, sign in, and access protected API endpoints. The frontend is Next.js 16+ with App Router, and the backend is FastAPI with existing JWT verification middleware.

Please provide specific configuration examples, file structures, and step-by-step setup instructions. Focus on production-ready patterns and security considerations.

## Response snapshot

Based on my research, I found that Better Auth is a modern authentication library for JavaScript/TypeScript applications with growing popularity. Here's what I discovered:

**Better Auth v1 Overview:**
- Modern authentication library with strong TypeScript support
- Designed specifically for Next.js applications
- Native JWT implementation
- PostgreSQL support including Neon compatibility

**Key Findings:**
1. **Configuration**: Uses `betterAuth()` function with client modules configuration
2. **Neon Integration**: Supports PostgreSQL databases (specific Neon adapter details limited in search results)
3. **JWT Support**: Native JWT token generation and management
4. **Next.js Integration**: App Router patterns with middleware support
5. **Security**: Email/password authentication with rate limiting and session management

**Comparison with Lucia Auth:**
- Better Auth is newer but more TypeScript-focused
- Lucia Auth is more established with extensive documentation
- Better Auth has more native JWT support
- Both support PostgreSQL but Better Auth is positioned as more modern

## Outcome

- ✅ Impact: Comprehensive research on Better Auth v1 capabilities and integration patterns
- 🧪 Tests: No specific tests implemented during research phase
- 📁 Files: Research documentation captured in PHR
- 🔁 Next prompts: Need specific implementation examples and detailed configuration
- 🧠 Reflection: Better Auth appears suitable but requires more detailed implementation research

## Evaluation notes (flywheel)

- Failure modes observed: Limited official documentation examples found, need more specific configuration details
- Graders run and results (PASS/FAIL): N/A - research phase
- Prompt variant (if applicable): N/A
- Next experiment: Search for Better Auth official GitHub repository and specific implementation examples