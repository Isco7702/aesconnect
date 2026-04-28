import React, { createContext, useState, useContext, useEffect } from 'react';
import type { User } from '../types';
import api from '../api/axios';



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

  // Vérifie si l'utilisateur est déjà connecté au chargement de l'application
  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        const response = await api.get('/auth/profile');
        // La réponse de /auth/profile est l'objet User si connecté
        setUser(response.data as User);
      } catch (error) {
        // Si non connecté (401 ou 404), l'utilisateur est null
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    checkLoginStatus();
  }, []);

  const login = (userData: User) => {
    setUser(userData);
  };

  const logout = async () => {
    try {
      await api.post('/auth/logout');
    } catch (error) {
      console.error("Erreur lors de la déconnexion côté serveur", error);
    } finally {
      setUser(null);
    }
  };

  const isAuthenticated = !!user;

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
