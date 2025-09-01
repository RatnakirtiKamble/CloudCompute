// src/Context/AuthContext.tsx
import { createContext, useContext, useEffect, useState } from "react";

interface User {
  id: number;
  username: string;
  email: string;
  role: string;
}

interface AuthContextType {
  accessToken: string | null;
  user: User | null;
  loading: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(
    localStorage.getItem("token")
  );
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  // Call whoami on mount
  useEffect(() => {
    const checkUser = async () => {
      if (!accessToken) {
        setLoading(false);
        return;
      }
      try {
        const res = await fetch("http://localhost:8000/auth/whoami", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
        });

        if (!res.ok) throw new Error("Invalid token");

        const data = await res.json();
        setUser(data);
      } catch (err) {
        console.error("Auth check failed", err);
        logout();
      } finally {
        setLoading(false);
      }
    };

    checkUser();
  }, [accessToken]);

  const login = async (token: string) => {
    localStorage.setItem("token", token);
    setAccessToken(token);
  
    try {
      const res = await fetch("http://localhost:8000/auth/whoami", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
  
      if (!res.ok) throw new Error("Invalid token");
  
      const data = await res.json();
      setUser(data);
    } catch (err) {
      console.error("Failed to fetch user after login", err);
      logout();
    }
  };
  

  const logout = () => {
    localStorage.removeItem("token");
    setAccessToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ accessToken, user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
