<div align="center">

# TODO EVOLUTION

### AI-Powered Task Management App

[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=flat-square&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![Supabase](https://img.shields.io/badge/Supabase-Auth%20%2B%20DB-3fcf8e?style=flat-square&logo=supabase)](https://supabase.com/)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-black?style=flat-square&logo=vercel)](https://vercel.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

A modern task management app with an AI chat assistant, built on Next.js and Supabase.

[Live Demo](#deployment) &bull; [Getting Started](#getting-started) &bull; [Features](#features)

</div>

---

## Features

- **Task Management** &mdash; Create, edit, delete, and complete tasks with priority levels
- **AI Chat Assistant** &mdash; Manage tasks through natural language via Groq-powered Taska AI
- **Authentication** &mdash; Sign up, sign in, and session management powered by Supabase Auth
- **Real-time** &mdash; Instant updates with Supabase's real-time subscriptions
- **Responsive UI** &mdash; Mobile-first design with Tailwind CSS

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Framework | Next.js 16 (App Router) |
| Language | TypeScript 5 |
| Styling | Tailwind CSS 4 |
| Auth & Database | Supabase (PostgreSQL + Auth + RLS) |
| AI Chat | Groq API (Llama 3.1) |
| State Management | TanStack React Query |
| Forms | React Hook Form + Zod |
| Deployment | Vercel |

## Architecture

```
Browser
  │
  ├── Supabase Client (direct)
  │     ├── Auth (sign-up, sign-in, sessions)
  │     └── Database (task CRUD via RLS)
  │
  └── Next.js API Routes (server-side)
        └── /api/chat → Groq API (AI assistant)
```

No separate backend server. The frontend talks directly to Supabase for auth and data, with Row Level Security ensuring users only access their own tasks. The AI chat runs as a Next.js serverless function.

## Getting Started

### Prerequisites

- [Node.js](https://nodejs.org/) 18+
- A [Supabase](https://supabase.com/) project
- A [Groq](https://console.groq.com/) API key (free tier available)

### 1. Clone and install

```bash
git clone https://github.com/iamKhan79690/TODO-EVOLUTION.git
cd TODO-EVOLUTION/frontend
npm install
```

### 2. Configure environment

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
NEXT_PUBLIC_APP_URL=http://localhost:3000
GROQ_API_KEY=your-groq-api-key
```

### 3. Set up Supabase

Run the SQL in `frontend/supabase-setup.sql` in your Supabase SQL Editor to create the tasks table and RLS policies.

### 4. Run locally

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Deployment

### Vercel (Recommended)

1. Import the repo on [vercel.com](https://vercel.com/new)
2. Set **Root Directory** to `frontend`
3. Add environment variables:

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_SUPABASE_URL` | Your Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Your Supabase anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | Your Supabase service role key |
| `NEXT_PUBLIC_APP_URL` | Your Vercel deployment URL |
| `GROQ_API_KEY` | Your Groq API key |

4. Deploy

## Project Structure

```
frontend/
  src/
    app/
      page.tsx              # Landing page
      dashboard/
        page.tsx            # Main task dashboard
        chat-widget.tsx     # AI chat assistant
      auth/
        signin/page.tsx     # Sign in
        signup/page.tsx     # Sign up
      api/
        chat/route.ts       # Groq AI endpoint
    lib/
      supabase/             # Supabase client setup
      api.ts                # Task API (Supabase queries)
      auth-provider.tsx     # Auth context
      types.ts              # TypeScript types
    middleware.ts            # Session management
```

## License

MIT

</div>
