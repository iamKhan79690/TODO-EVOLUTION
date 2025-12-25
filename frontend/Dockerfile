# Multi-stage build for production-ready Next.js 16 application
# Following Phase IV Constitutional requirements

# Stage 1: Dependencies
FROM node:20-alpine AS dependencies
# Add labels for constitutional compliance
LABEL maintainer="TODO Evolution Team" \
      version="1.0.0" \
      description="Dependencies stage for Next.js frontend"

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install --only=production && npm cache clean --force

# Stage 2: Build
FROM node:20-alpine AS builder
# Add labels for constitutional compliance
LABEL maintainer="TODO Evolution Team" \
      version="1.0.0" \
      description="Build stage for Next.js frontend"

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies)
# Use --ignore-scripts to skip platform-specific binaries during install
RUN npm install --ignore-optional || npm install --legacy-peer-deps

# Copy source code
COPY . .

# Set environment variables for build time
ENV NEXT_PUBLIC_API_URL=/api/proxy \
    NEXT_PUBLIC_FASTAPI_URL=/api/proxy \
    NEXT_PUBLIC_CHAT_API_URL=/api/proxy \
    NEXT_PUBLIC_AUTH_URL=/api/proxy \
    NEXT_PUBLIC_APP_URL=http://127.0.0.1:43321

# Build the application
RUN npm run build

# Remove development dependencies
RUN npm prune --production

# Stage 3: Runtime
FROM node:20-alpine AS runtime
# Add labels for constitutional compliance
LABEL maintainer="TODO Evolution Team" \
      version="1.0.0" \
      description="Production Next.js frontend runtime" \
      org.label-schema.name="todo-frontend" \
      org.label-schema.version="1.0.0" \
      org.label-schema.schema-version="1.0"

# Security: Create non-root user
RUN addgroup -g 1001 -S appuser && \
    adduser -S nextjs -u 1001 -G appuser

WORKDIR /app

# Copy built application from builder stage
COPY --from=builder --chown=1001:1001 /app/public ./public
COPY --from=builder --chown=1001:1001 /app/.next/standalone ./
COPY --from=builder --chown=1001:1001 /app/.next/static ./.next/static
COPY --from=builder --chown=1001:1001 /app/package*.json ./
COPY --from=builder --chown=1001:1001 /app/node_modules ./node_modules

# Create necessary directories with proper permissions
RUN mkdir -p /app/.next/cache && \
    chown -R 1001:1001 /app/.next

# Switch to non-root user
USER nextjs

# Environment variables
ENV NODE_ENV=production \
    PORT=3000 \
    NEXT_PUBLIC_API_URL=/api/proxy \
    NEXT_PUBLIC_FASTAPI_URL=/api/proxy \
    NEXT_PUBLIC_CHAT_API_URL=/api/proxy \
    NEXT_PUBLIC_AUTH_URL=/api/proxy \
    NEXT_PUBLIC_APP_URL=http://127.0.0.1:43321

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/api/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })" || \
  curl -f http://localhost:3000/api/health || exit 1

# Start the application
CMD ["npm", "start"]