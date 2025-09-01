import { useState } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../Context/AuthContext";

export default function AuthPage() {
  const { login } = useAuth()
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [formData, setFormData] = useState({ email: "", username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [invalidMessage, setInvalidMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  const toggleMode = () => {
    setMode(mode === "signin" ? "signup" : "signin");
    setInvalidMessage(null);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setInvalidMessage(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setInvalidMessage(null);

    try {
      if (mode === "signup") {
        await axios.post("http://localhost:8000/auth/register", {
          email: formData.email,
          username: formData.username,
          password: formData.password,
        });

        const loginRes = await axios.post(
          "http://localhost:8000/auth/login",
          new URLSearchParams({
            username: formData.email,
            password: formData.password,
          }),
          { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
        );

        await login(loginRes.data.access_token)
        navigate("/dashboard");
      } else {
        const loginRes = await axios.post(
          "http://localhost:8000/auth/login",
          new URLSearchParams({
            username: formData.email,
            password: formData.password,
          }),
          { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
        );

        await login(loginRes.data.access_token)
        navigate("/dashboard");
      }
    } catch (err: any) {
      if (err.response?.status === 401) {
        setInvalidMessage("Invalid credentials");
      } else {
        setInvalidMessage("Internal server error");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen w-screen bg-gray-50">
      {/* Left Side */}
      <div className="hidden md:flex md:w-1/2 bg-gradient-to-br from-blue-600 to-indigo-700 items-center justify-center text-white p-10">
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
        >
          {mode === "signin" ? <h1 className="text-4xl font-bold mb-4">Welcome back to CloudFlow</h1> : <h1 className="text-4xl font-bold mb-4">Welcome to CloudFlow</h1> }
          <p className="text-lg max-w-md">
            Deploy your apps, manage compute workloads, and host static websites seamlessly.
          </p>
        </motion.div>
      </div>

      {/* Right Side */}
      <div className="flex md:w-1/2 items-center justify-center p-8">
        <div className="bg-white shadow-xl rounded-2xl p-8 w-full max-w-md">
          <h2 className="text-2xl font-bold mb-6 text-center">
            {mode === "signin" ? "Sign In" : "Create Account"}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === "signup" && (
              <input
                type="text"
                name="username"
                placeholder="Username"
                value={formData.username}
                onChange={handleChange}
                required
                className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            )}
            <input
              type="email"
              name="email"
              placeholder="Email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleChange}
              required
              className="w-full border rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {invalidMessage && <p className="text-red-500 text-sm">{invalidMessage}</p>}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition duration-200"
            >
              {loading ? "Loading..." : mode === "signin" ? "Sign In" : "Sign Up"}
            </button>
          </form>
          <p className="text-center mt-4 text-sm text-gray-600">
            {mode === "signin" ? (
              <>
                Don't have an account?{" "}
                <span
                  onClick={toggleMode}
                  className="text-blue-600 cursor-pointer hover:underline"
                >
                  Sign Up
                </span>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <span
                  onClick={toggleMode}
                  className="text-blue-600 cursor-pointer hover:underline"
                >
                  Sign In
                </span>
              </>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
