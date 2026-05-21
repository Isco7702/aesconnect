import React, { createContext, useState, useContext, useEffect } from 'react';
import type { User } from '../types';
import api from '../api/axios';

const AUTH_USER_ID_KEY = 'aesconnect_user_id';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (userData: User) => void;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const restoreLocalUser = () => {
      const storedUserId = localStorage.getItem(AUTH_USER_ID_KEY);
      if (!storedUserId) {
        return;
      }

      setUser((currentUser) => {
        if (currentUser) {
          return currentUser;
        }

        return {
          id: Number(storedUserId),
          username: '',
          full_name: '',
          email: '',
          city: '',
          country: '',
          avatar_url: '',
          is_admin: false,
        };
      });
    };

    const checkLoginStatus = async () => {
      restoreLocalUser();

      try {
        const response = await api.get('/auth/profile');
        const profileUser = response.data as User;
        setUser(profileUser);
        localStorage.setItem(AUTH_USER_ID_KEY, String(profileUser.id));
      } catch (error) {
        // If profile check fails, keep the restored local user (if present)
      } finally {
        setLoading(false);
      }
    };

    checkLoginStatus();
  }, []);

  const login = (userData: User) => {
    setUser(userData);
    localStorage.setItem(AUTH_USER_ID_KEY, String(userData.id));
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error('Erreur lors de la déconnexion côté serveur', error);
    } finally {
      setUser(null);
      localStorage.removeItem(AUTH_USER_ID_KEY);
    }
  };

  const isAuthenticated = !!user?.id;

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth doit être utilisé dans un AuthProvider');
  }
  return context;
};
