import { NextRequest, NextResponse } from 'next/server';

/**
 * API Proxy Route
 *
 * Proxies all requests from the browser to the backend service.
 * This solves the browser-to-Kubernetes connectivity issue because:
 * 1. Browser calls Next.js API routes (server-side)
 * 2. Next.js server-side code can access internal Kubernetes services
 * 3. No need to expose backend service externally
 *
 * Usage: Client-side code calls /api/proxy/* instead of backend URLs
 */

// Backend service URL from environment variable (internal K8s service name)
const BACKEND_URL = process.env.BACKEND_URL || 'http://todo-evolution-backend:8000';

export async function GET(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  return proxyRequest(request, path, 'GET');
}

export async function POST(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  return proxyRequest(request, path, 'POST');
}

export async function PUT(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  return proxyRequest(request, path, 'PUT');
}

export async function PATCH(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  return proxyRequest(request, path, 'PATCH');
}

export async function DELETE(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  return proxyRequest(request, path, 'DELETE');
}

async function proxyRequest(
  request: NextRequest,
  pathSegments: string[] | undefined,
  method: string
): Promise<NextResponse> {
  try {
    // Build the backend URL
    if (!pathSegments || pathSegments.length === 0) {
      return NextResponse.json(
        { error: 'Invalid path', message: 'No path provided', backend_url: BACKEND_URL },
        { status: 400 }
      );
    }

    const path = pathSegments.join('/');
    const url = `${BACKEND_URL}/${path}`;
    console.log(`Proxying ${method} request to: ${url}`);

    // Get query string from original request
    const queryString = request.nextUrl.search;

    // Clone the request headers and add any necessary headers
    const headers = new Headers();
    request.headers.forEach((value, key) => {
      headers.set(key, value);
    });

    // Add authorization header if token exists in cookies
    const token = request.cookies.get('access_token')?.value;
    if (token) {
      headers.set('Authorization', `Bearer ${token}`);
    }

    // Get request body for non-GET requests
    let body: RequestInit | undefined;
    if (method !== 'GET' && method !== 'HEAD') {
      body = {
        body: request.body,
      };
    }

    // Make the request to the backend
    const backendResponse = await fetch(`${url}${queryString}`, {
      method,
      headers,
      ...body,
      // @ts-ignore - Next.js types don't support duplex option
      duplex: 'half',
    });

    // Clone backend response headers
    const responseHeaders = new Headers();
    backendResponse.headers.forEach((value, key) => {
      // Skip certain headers that can cause issues
      if (
        key.toLowerCase() !== 'transfer-encoding' &&
        key.toLowerCase() !== 'connection' &&
        key.toLowerCase() !== 'keep-alive'
      ) {
        responseHeaders.set(key, value);
      }
    });

    // Add CORS headers
    responseHeaders.set('Access-Control-Allow-Origin', '*');
    responseHeaders.set('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS');
    responseHeaders.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

    // Return the response from the backend
    return new NextResponse(backendResponse.body, {
      status: backendResponse.status,
      statusText: backendResponse.statusText,
      headers: responseHeaders,
    });
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      {
        error: 'Proxy error',
        message: error instanceof Error ? error.message : 'Unknown error',
        backend_url: BACKEND_URL,
      },
      { status: 502 }
    );
  }
}

// Handle OPTIONS request for CORS preflight
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, PUT, PATCH, DELETE, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization',
    },
  });
}
