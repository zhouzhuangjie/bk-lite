'use client';

import { useSession, signIn } from 'next-auth/react';
import { useTranslation } from '@/utils/i18n';
import { createContext, useContext, useEffect, useState } from 'react';
import Spin from '@/components/spin';
import { useLocale } from '@/context/locale';

interface AuthContextType {
  token: string | null;
}

const AuthContext = createContext<AuthContextType | null>(null);

const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const { data: session, status } = useSession();
  const { t } = useTranslation();
  const { setLocale: changeLocale } = useLocale();
  const [token, setToken] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    if (status === 'loading') return;
    console.log('session:', session);
    if (!session) {
      signIn('keycloak');
      return;
    }
    if (session?.accessToken) {
      setToken(session.accessToken);
      setIsAuthenticated(true);
      const userLocale = session.locale || 'en';
      const savedLocale = localStorage.getItem('locale') || 'en';
      if (userLocale !== savedLocale) {
        changeLocale(userLocale);
      }
      localStorage.setItem('locale', userLocale);
    } else {
      console.warn(t('common.noAccessToken'));
    }
  }, [status]);

  if (status === 'loading' || !isAuthenticated) {
    return (
      <Spin></Spin>
    );
  }

  return (
    <AuthContext.Provider value={{ token }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

export default AuthProvider;
