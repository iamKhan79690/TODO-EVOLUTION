# Database Setup Guide

## Overview
This guide covers setting up Neon PostgreSQL for the Phase II Todo Evolution web application.

## Prerequisites
- Neon Tech account (free tier available)
- Git repository access

## Step 1: Create Neon Database

1. **Sign up for Neon**: Visit [https://neon.tech](https://neon.tech) and create an account
2. **Create Project**:
   - Click "New Project"
   - Choose PostgreSQL version (latest recommended)
   - Select region closest to you
   - Name your project (e.g., "todo-evolution")
3. **Get Connection String**:
   - Go to Dashboard → Connection Details
   - Copy the connection string
   - Format: `postgresql://username:password@ep-xyz.us-east-2.aws.neon.tech/dbname?sslmode=require`

## Step 2: Configure Environment

1. **Copy environment template**:
   ```bash
   cp .env.local.example .env.local
   ```

2. **Update DATABASE_URL** in `.env.local`:
   ```env
   DATABASE_URL=postgresql://your-username:your-password@ep-xyz.us-east-2.aws.neon.tech/your-dbname?sslmode=require
   ```

3. **Generate secure secrets**:
   ```bash
   # Generate Better Auth secret
   openssl rand -base64 32

   # Generate JWT secret
   openssl rand -base64 32
   ```

4. **Update secrets in `.env.local`**:
   ```env
   BETTER_AUTH_SECRET=your-generated-secret-here
   JWT_SECRET=your-jwt-secret-here
   ```

## Step 3: Database Schema

The application will automatically create the following tables on first run:

### Users Table (managed by Better Auth)
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Tasks Table (application data)
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high')),
    completed BOOLEAN DEFAULT FALSE,
    due_date TIMESTAMP,
    tags TEXT[] DEFAULT '{}',
    recurrence_rule TEXT,
    reminder_config TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Step 4: Verify Connection

1. **Start backend server**:
   ```bash
   cd backend
   source venv/bin/activate  # Windows: venv\Scripts\activate
   uvicorn main:app --reload
   ```

2. **Test database connection**:
   - Visit http://localhost:8000/health
   - Should return healthy status if database is connected

## Step 5: Manage Database (Optional)

### Access Neon Console
- Go to your Neon project dashboard
- Use the "SQL Editor" to run queries
- View table structure and data

### Common Operations
```sql
-- View all tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';

-- View users
SELECT * FROM users;

-- View tasks
SELECT * FROM tasks;

-- Reset database (careful!)
DROP TABLE IF EXISTS tasks CASCADE;
```

## Troubleshooting

### Connection Issues
- **Problem**: "Connection refused" or timeout
- **Solution**: Verify DATABASE_URL format and network connectivity

### SSL Issues
- **Problem**: SSL handshake failed
- **Solution**: Ensure `?sslmode=require` is in connection string

### Permission Issues
- **Problem**: "Permission denied" errors
- **Solution**: Check database user permissions in Neon console

### Environment Variables
- **Problem**: Environment variables not loading
- **Solution**: Verify `.env.local` exists and has correct format

## Best Practices

1. **Never commit `.env.local`** to version control
2. **Use different databases** for development and production
3. **Regular backups** - Neon handles this automatically
4. **Monitor usage** - Check Neon dashboard for resource usage

## Support

- **Neon Documentation**: https://neon.tech/docs
- **Project Issues**: Create GitHub issue in repository
- **Community**: Join project Discord/Slack for help