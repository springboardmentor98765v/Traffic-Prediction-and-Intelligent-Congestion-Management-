"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { api, tokenStorage, UserProfile, AuthResponse } from "./api";

interface AuthContextType {
  user: UserProfile | null;
  role: string;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<AuthResponse>;
  register: (name: string, email: string, password: string, role: string) => Promise<UserProfile>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    // Hydrate auth state from localStorage on client mount
    const storedToken = tokenStorage.getToken();
    const storedUser = tokenStorage.getUser();

    if (storedToken) {
      setToken(storedToken);
      if (storedUser) {
        setUser(storedUser);
      }
      // Validate token with /me endpoint in background
      api.getMe()
        .then((profile) => {
          setUser(profile);
          tokenStorage.setUser(profile);
        })
        .catch(() => {
          // Token expired or invalid
          tokenStorage.clear();
          setToken(null);
          setUser(null);
        })
        .finally(() => setIsLoading(false));
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (email: string, password: string): Promise<AuthResponse> => {
    const authData = await api.login(email, password);
    tokenStorage.setTokens(authData.access_token, authData.refresh_token);
    setToken(authData.access_token);

    // Fetch and store user profile
    try {
      const profile = await api.getMe();
      setUser(profile);
      tokenStorage.setUser(profile);
    } catch {
      // Fallback profile from login role
      const fallback: UserProfile = {
        user_id: "me",
        name: email.split("@")[0],
        email,
        role: authData.role || "public",
      };
      setUser(fallback);
      tokenStorage.setUser(fallback);
    }

    return authData;
  };

  const register = async (name: string, email: string, password: string, role: string): Promise<UserProfile> => {
    return api.register(name, email, password, role);
  };

  const logout = () => {
    tokenStorage.clear();
    setToken(null);
    setUser(null);
  };

  const refreshProfile = async () => {
    if (!tokenStorage.getToken()) return;
    try {
      const profile = await api.getMe();
      setUser(profile);
      tokenStorage.setUser(profile);
    } catch {
      logout();
    }
  };

  const role = user?.role ? user.role.toLowerCase() : "public";

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        token,
        isAuthenticated: !!token,
        isLoading,
        login,
        register,
        logout,
        refreshProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
