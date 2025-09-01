import { Navigate, useLocation } from "react-router-dom";
import { type ReactNode } from "react";
import { useAuth } from "../Context/AuthContext";

interface ProtectedRouteProps {
  children: ReactNode;
}

/**
 * ProtectedRoute
 * --------------
 * Wraps routes that require authentication.
 * - Shows a loading screen while verifying the session.
 * - Redirects unauthenticated users to `/` (Home) with their intended
 *   location in state, so they can be redirected back after logging in.
 * - Renders children if authenticated.
 */
function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { accessToken, user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen text-white text-2xl">
        Loading...
      </div>
    );
  }

  if (!accessToken || !user) {
    return <Navigate to="/" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}


export default ProtectedRoute;
