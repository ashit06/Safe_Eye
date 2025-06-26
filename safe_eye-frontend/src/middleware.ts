import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // Check if the request is for the login page
  if (request.nextUrl.pathname === '/login' || request.nextUrl.pathname === '/') {
    return NextResponse.next();
  }

  // Check for authentication token in cookies or headers
  const token = request.cookies.get('accessToken')?.value || 
                request.headers.get('Authorization')?.replace('Bearer ', '');

  // If no token is found and trying to access protected routes, redirect to login
  if (!token && (
    request.nextUrl.pathname.startsWith('/dashboard') ||
    request.nextUrl.pathname.startsWith('/surveillance-view') ||
    request.nextUrl.pathname.startsWith('/event-records') ||
    request.nextUrl.pathname.startsWith('/alert-panel') ||
    request.nextUrl.pathname.startsWith('/system-settings')
  )) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/dashboard/:path*',
    '/surveillance-view/:path*', 
    '/event-records/:path*', 
    '/alert-panel/:path*', 
    '/system-settings/:path*',
    '/login',
    '/'
  ],
};
