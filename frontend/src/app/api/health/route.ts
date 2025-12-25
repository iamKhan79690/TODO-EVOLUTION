import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // Check if frontend is healthy
    const isHealthy = true; // Basic health check

    if (isHealthy) {
      return NextResponse.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: 'todo-frontend',
        version: '1.0.0',
        uptime: process.uptime()
      });
    } else {
      return NextResponse.json({
        status: 'unhealthy',
        timestamp: new Date().toISOString(),
        service: 'todo-frontend'
      }, { status: 500 });
    }
  } catch (error) {
    return NextResponse.json({
      status: 'error',
      timestamp: new Date().toISOString(),
      service: 'todo-frontend',
      error: 'Health check failed'
    }, { status: 500 });
  }
}