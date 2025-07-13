'use client';

import { useState, FormEvent, ChangeEvent } from "react";
import { useRouter } from "next/navigation";
import api from '@/lib/api'; // Use the centralized api instance
import { AxiosError } from "axios"; // Keep for detailed error checking

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Shield, Eye, EyeOff } from "lucide-react";
import { storeAuthTokens } from "@/lib/auth";

interface LoginResponse {
  access: string;
  refresh: string;
}

export default function LoginForm() {
  const [showPassword, setShowPassword] = useState(false);
  const [credentials, setCredentials] = useState({
    username: "admin", // Pre-filled for demo purposes
    password: "admin123", // Pre-filled for demo purposes
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const router = useRouter();

  const handleLogin = async (e: FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    try {
      // Use the 'api' instance. The full URL is no longer needed.
      const response = await api.post<LoginResponse>('/token/', credentials);

      storeAuthTokens(response.data.access, response.data.refresh);
      router.push("/dashboard");
    } catch (err) {
      console.error("Login error:", err);
      // Update the error check to use instanceof
      if (err instanceof AxiosError) {
        if (err.response?.status === 401) {
          setError("Invalid username or password. Please try again.");
        } else if (err.response?.status === 400) {
          setError("Please provide both username and password.");
        } else if (!err.response) {
          setError("Unable to connect to the server. Check your connection.");
        } else {
          setError("An unexpected error occurred. Please try again.");
        }
      } else {
        setError("An error occurred. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const { id, value } = e.target;
    setCredentials((prev) => ({ ...prev, [id]: value }));
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900">
      <Card className="w-full max-w-md mx-4">
        <CardHeader className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-blue-100">
            <Shield className="h-8 w-8 text-blue-600" />
          </div>
          <CardTitle className="text-2xl font-bold">Smart Road Safety System</CardTitle>
          <CardDescription>Administrator Access Portal</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="mb-4 text-sm text-gray-600 text-center bg-yellow-100 p-2 rounded-md">
            <p>
              <strong>Demo Login:</strong>{" "}
              <span className="font-mono">admin / admin123</span>
            </p>
            <p className="mt-1 text-xs text-red-700">
              Note: This portal is strictly for administrative use only.
            </p>
          </div>

          <form onSubmit={handleLogin} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                placeholder="Enter your username"
                value={credentials.username}
                onChange={handleChange}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  value={credentials.password}
                  onChange={handleChange}
                  required
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>

            {error && <div className="text-red-500 text-sm">{error}</div>}

            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Authenticating..." : "Sign In"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}