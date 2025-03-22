import { JWT, getToken } from 'next-auth/jwt';
import { NextRequest, NextResponse } from 'next/server';

// Helper function to generate logout parameters
function logoutParams(token: JWT): Record<string, string> {
  return {
    id_token_hint: token.idToken as string,
    post_logout_redirect_uri: process.env.NEXTAUTH_URL as string,
  };
}

// Handle the actual logout API
export const POST = async (req: NextRequest) => {
  try {
    console.log('Received POST request for logout.');

    // Attempt to get the JWT from the request
    const token = await getToken({ req });
    if (!token) {
      console.warn('No token found in the session.');
      return NextResponse.json(
        { message: 'No session found', error: 'Unauthorized' },
        { status: 401 }
      );
    }

    const endSessionEndpoint = new URL(
      `${process.env.KEYCLOAK_ISSUER}/protocol/openid-connect/logout`
    );

    const params = new URLSearchParams(logoutParams(token));
    console.log('Logout URL parameters:', params.toString());

    // Redirect user to the Keycloak logout URL
    const logoutURL = `${endSessionEndpoint}?${params}`;
    return NextResponse.json({ url: logoutURL }, { status: 200 });
  } catch (error) {
    console.error('Logout error:', error);
    return NextResponse.json(
      { message: 'Logout processing failed' },
      { status: 500 }
    );
  }
};

// Optional: Handle GET requests for debugging or miscommunication
export const GET = async () => {
  return NextResponse.json({ message: 'Method Not Allowed' }, { status: 405 });
};

// Export to force dynamic behavior
export const dynamic = 'force-dynamic';
