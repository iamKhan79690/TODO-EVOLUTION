---
id: 001
title: Frontend Constitution Creation
stage: constitution
date: 2025-12-04
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: 003-recurring-tasks-due-dates
user: Principal Frontend Architect
command: /sp.constitution
labels: ["constitution", "frontend", "governance", "phase-ii"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - frontend/CLAUDE.md (created)
  - .specify/memory/constitution.md (updated)
tests:
  - No tests created - governance documentation only
---

## Prompt

Act as a Principal Frontend Architect. I need you to generate the "Frontend Constitution" file that will govern all AI development in the `frontend/` directory.

Please create the file `frontend/CLAUDE.md` with the following strict specialized rules:

# FILE: frontend/CLAUDE.md

## 🤖 Role: Frontend Specialist Agent
You are an expert in **Next.js 16 (App Router)**, **TypeScript**, **Tailwind CSS**, and **Better Auth**.
Your goal is to build a responsive, accessible, and type-safe UI that strictly adheres to the specifications in `@specs/ui/`.

## 🧠 Core Intelligence & Skills
1.  **Server-First Mentality:** Use React Server Components (RSC) by default. Only use `"use client"` for interactive leaves (buttons, forms).
2.  **Reusable Component Architecture:**
    - Build atomic components in `/components/ui/` (Buttons, Inputs).
    - Build feature components in `/components/features/` (TaskCard, LoginForm).
    - Never duplicate styles; use Tailwind utility classes.
3.  **Type-Safe Communication:**
    - Never use `fetch` directly in components.
    - ALWAYS use the typed client in `lib/api-client.ts`.
    - Share types with the backend via a shared types file or by manually keeping interfaces in sync with `@specs/database/schema.md`.

## 🛡️ Integration Standards (Better Auth)
- **Auth Flow:** Use `better-auth/react` hooks (`useSession`) for client-side auth state.
- **Security:** Ensure every API request to the backend includes the JWT token in the header: `Authorization: Bearer <token>`.
- **Middleware:** Use `middleware.ts` to protect private routes (e.g., `/dashboard`).

## ⚡ Workflow Rules
1.  **Read First:** Before writing code, read the UI spec: `read_file @specs/ui/<feature>.md`.
2.  **Mobile First:** All designs must be responsive. Use `md:` and `lg:` modifiers.
3.  **Icons:** Use `lucide-react` for all iconography.

## 🚀 Initialization Command
(If the folder is empty, run this implementation plan immediately):
1.  `npx create-next-app@latest frontend --typescript --tailwind --eslint`
2.  `npm install better-auth lucide-react clsx tailwind-merge`
3.  Create `lib/utils.ts` for class merging.
4.  Create `lib/api-client.ts` template.

## Response snapshot

Created the Frontend Constitution file (`frontend/CLAUDE.md`) with comprehensive frontend-specific governance rules and updated the main project constitution to reflect the new Phase II full-stack architecture with agent-specialized development.

### Key Changes Made:

1. **Frontend Constitution Created**: `frontend/CLAUDE.md` with specialized rules for:
   - Next.js 16 App Router expertise
   - React Server Components first approach
   - TypeScript strict mode requirements
   - Tailwind CSS utility-first styling
   - Better Auth integration standards
   - Type-safe API communication patterns

2. **Main Constitution Updated**: `.specify/memory/constitution.md` to reflect:
   - Transition from Phase I to Phase II (console → full-stack web)
   - Monorepo structure with backend/frontend separation
   - Agent-specialized development model
   - Updated tech stack (FastAPI + Next.js + PostgreSQL)
   - Enhanced quality standards for full-stack development
   - New Phase II constraints and success criteria

3. **Template Synchronization**: Verified compatibility with existing SpecKit templates and updated governance structure.

## Outcome

- ✅ Impact: Established comprehensive governance for frontend development with specialized agent model
- 🧪 Tests: No tests required - governance documentation update
- 📁 Files: Created `frontend/CLAUDE.md`, updated `.specify/memory/constitution.md`
- 🔁 Next prompts: Recommend creating `backend/CLAUDE.md` constitution, then proceed with Phase II feature specifications
- 🧠 Reflection: Successfully transitioned project governance from single-agent to multi-agent specialized model for full-stack development

## Evaluation notes (flywheel)

- Failure modes observed: None - governance update completed successfully
- Graders run and results (PASS/FAIL): No graders applicable - documentation only
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create backend specialist constitution to complete the agent specialization model