import KeycloakProvider from "next-auth/providers/keycloak";
import { AuthOptions } from "next-auth";
import { JWT } from "next-auth/jwt";

async function requestRefreshOfAccessToken(token: JWT) {
  const response = await fetch(`${process.env.KEYCLOAK_ISSUER}/protocol/openid-connect/token`, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({
      client_id: process.env.KEYCLOAK_CLIENT_ID!,
      client_secret: process.env.KEYCLOAK_CLIENT_SECRET!,
      grant_type: "refresh_token",
      refresh_token: token.refreshToken! as string,
    }),
    method: "POST",
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to refresh access token");
  }

  return response.json();
}

async function introspectToken(token: string) {
  const response = await fetch(
    `${process.env.KEYCLOAK_ISSUER}/protocol/openid-connect/token/introspect`,
    {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        client_id: process.env.KEYCLOAK_CLIENT_ID!,
        client_secret: process.env.KEYCLOAK_CLIENT_SECRET!,
        token,
      }),
      method: "POST",
      cache: "no-store",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to introspect token");
  }

  return response.json();
}

async function fetchUserRolesAndLocale(accessToken: string) {
  try {
    const introspectData = await introspectToken(accessToken);
    return {
      locale: introspectData.locale || 'en',
      roles: introspectData.realm_access.roles || [],
      username: introspectData.username || '',
      zoneinfo: introspectData.zoneinfo || 'utc',
    };
  } catch (error) {
    console.error("Error introspecting token", error);
    return {
      locale: 'en',
      roles: [],
      username: '',
      zoneinfo: 'utc'
    };
  }
}

export const authOptions: AuthOptions = {
  providers: [
    KeycloakProvider({
      clientId: process.env.KEYCLOAK_CLIENT_ID!,
      clientSecret: process.env.KEYCLOAK_CLIENT_SECRET!,
      issuer: process.env.KEYCLOAK_ISSUER!,
    }),
  ],
  pages: {
    signIn: '/auth/signin',
    signOut: '/auth/signout',
  },
  session: {
    strategy: "jwt",
    maxAge: 60 * 60 * 24,
  },
  callbacks: {
    async jwt({ token, account }) {
      if (account) {
        token.idToken = account.id_token;
        token.accessToken = account.access_token;
        token.refreshToken = account.refresh_token;
        token.expiresAt = account.expires_at;

        if (token.accessToken) {
          try {
            const userInfo = await fetchUserRolesAndLocale(token.accessToken);
            token.locale = userInfo.locale || 'en';
            token.roles = userInfo.roles || [];
            token.username = userInfo.username || '';
            token.zoneinfo = userInfo.zoneinfo || 'utc';
          } catch (error) {
            console.error("Error fetching user info", error);
          }
        }
        return token;
      }

      const expiresAt = token.expiresAt ? Number(token.expiresAt) : 0;
      if (Date.now() < expiresAt * 1000 - 60 * 1000) {
        return token;
      } else {
        try {
          const tokens = await requestRefreshOfAccessToken(token);

          const updatedToken: JWT = {
            ...token,
            idToken: tokens.id_token,
            accessToken: tokens.access_token,
            expiresAt: Math.floor(Date.now() / 1000 + (tokens.expires_in as number)),
            refreshToken: tokens.refresh_token ?? token.refreshToken,
          };
          try {
            const userInfo = await fetchUserRolesAndLocale(updatedToken?.accessToken ?? '');
            updatedToken.locale = userInfo.locale || 'en';
            updatedToken.username = userInfo.username || '';
            updatedToken.roles = userInfo.roles || [];
            updatedToken.zoneinfo = userInfo.zoneinfo || 'utc';
          } catch (error) {
            console.error("Error fetching user info", error);
          }

          return updatedToken;
        } catch (error) {
          console.error("Error refreshing access token", error);
          return { ...token, error: "RefreshAccessTokenError" };
        }
      }
    },
    async session({ session, token }) {
      if (token.accessToken) {
        session.accessToken = token.accessToken;
      }
      if (token.error) {
        session.error = token.error;
      }
      if (token.username) {
        session.username = token.username;
      }
      if (token.locale) {
        session.locale = token.locale;
      }
      if (token.roles) {
        session.roles = token.roles;
      }
      if (token.zoneinfo) {
        session.zoneinfo = token.zoneinfo;
      }
      return session;
    },
  },
};
