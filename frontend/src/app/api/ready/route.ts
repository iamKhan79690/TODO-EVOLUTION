import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // Check if frontend is ready to serve traffic
    // This could include checking for required environment variables
    const requiredEnvVars = ['NEXT_PUBLIC_API_URL'];
    const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

    if (missingVars.length > 0) {
      return NextResponse.json({
        status: 'not_ready',
        timestamp: new Date().toISOString(),
        service: 'todo-frontend',
        reason: `Missing environment variables: ${missingVars.join(', ')}`
      }, { status: 503 });
    }

    return NextResponse.json({
      status: 'ready',
      timestamp: new Date().toISOString(),
      service: 'todo-frontend',
      version: '1.0.0',
      environment: process.env.NODE_ENV || 'unknown'
    });
  } catch (error) {
    return NextResponse.json({
      status: 'not_ready',
      timestamp: new Date().toISOString(),
      service: 'todo-frontend',
      error: 'Readiness check failed'
    }, { status: 503 });
  }
}