"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { api, tokenStorage, UserProfile } from "./api";

interface AuthContextType {
  user: UserProfile | null;
  role: "admin" | "operator" | "public";
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isSimulationMode: boolean;
  toggleSimulationMode: () => void;
  login: (email: string, password: string) => Promise<void>;
  loginAsDemo: (demoRole: "admin" | "operator" | "public") => Promise<void>;
  register: (name: string, email: string, password: string, role?: string) => Promise<void>;
  logout: () => void;
  setRoleOverride: (role: "admin" | "operator" | "public") => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserProfile | null>(null);
  const [role, setRole] = useState<"admin" | "operator" | "public">("operator");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSimulationMode, setIsSimulationMode] = useState<boolean>(false);

  useEffect(() => {
    // Hydrate from localStorage
    const storedToken = tokenStorage.getToken();
    const storedUser = tokenStorage.getUser();
    setIsSimulationMode(tokenStorage.isSimulationMode());

    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(storedUser);
      setRole((storedUser.role?.toLowerCase() as "admin" | "operator" | "public") || "operator");
    } else {
      // Default initial session for ease of demonstration
      const demoUser: UserProfile = {
        user_id: "usr_demo_admin",
        name: "Director Harris",
        email: "admin@trafficvision.ai",
        role: "admin",
      };
      setToken("demo_token_init");
      setUser(demoUser);
      setRole("admin");
      tokenStorage.setTokens("demo_token_init");
      tokenStorage.setUser(demoUser);
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await api.login(email, password);
      tokenStorage.setTokens(res.access_token, res.refresh_token);
      tokenStorage.setUser(res.user);
      setToken(res.access_token);
      setUser(res.user);
      setRole((res.role.toLowerCase() as "admin" | "operator" | "public") || "operator");
    } finally {
      setIsLoading(false);
    }
  };

  const loginAsDemo = async (demoRole: "admin" | "operator" | "public") => {
    setIsLoading(true);
    try {
      const email = `${demoRole}@trafficvision.ai`;
      const res = await api.login(email, "demo123456");
      tokenStorage.setTokens(res.access_token, res.refresh_token);
      const profile: UserProfile = {
        user_id: `usr_${demoRole}_${Date.now()}`,
        name: demoRole === "admin" ? "Admin Supervisor" : demoRole === "operator" ? "Duty Operator" : "Commuter Portal",
        email,
        role: demoRole,
      };
      tokenStorage.setUser(profile);
      setToken(res.access_token);
      setUser(profile);
      setRole(demoRole);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (name: string, email: string, password: string, regRole: string = "operator") => {
    setIsLoading(true);
    try {
      const newUser = await api.register(name, email, password, regRole);
      await login(email, password);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    tokenStorage.clear();
    setToken(null);
    setUser(null);
    setRole("public");
  };

  const setRoleOverride = (newRole: "admin" | "operator" | "public") => {
    setRole(newRole);
    if (user) {
      const updated = { ...user, role: newRole };
      setUser(updated);
      tokenStorage.setUser(updated);
    }
  };

  const toggleSimulationMode = () => {
    const next = !isSimulationMode;
    setIsSimulationMode(next);
    tokenStorage.setSimulationMode(next);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        token,
        isAuthenticated: !!token,
        isLoading,
        isSimulationMode,
        toggleSimulationMode,
        login,
        loginAsDemo,
        register,
        logout,
        setRoleOverride,
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
