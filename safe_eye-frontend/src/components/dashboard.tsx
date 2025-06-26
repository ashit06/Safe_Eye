'use client';

import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Camera as CameraIcon,
  AlertTriangle,
  Shield,
  Clock,
  MapPin,
  Bell,
  LogOut,
} from "lucide-react";

import LiveDetection from "@/components/UnifiedDetection";
import EventRecords from "@/components/event-records";
import AlertPanel from "@/components/alert-panel";
import SystemSettings from "@/components/system-settings";

import { getAuthToken, clearAuthData } from "@/lib/auth";

export default function DashboardPage() {
  const [activeAlerts, setActiveAlerts] = useState(0);
  const [eventsToday, setEventsToday] = useState(0);
  const [cameras, setCameras] = useState(0);
  const [coverageAreas, setCoverageAreas] = useState(0);
  const [systemStatus, setSystemStatus] = useState<"Active" | "Error">("Active");
  const [defaultTab] = useState<"detection">("detection");
  const router = useRouter();
  const token = getAuthToken();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!token) {
      clearAuthData();
      router.push("/login");
    }
  }, [router, token]);

  // Fetch stats
  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        const res = await axios.get("http://127.0.0.1:8000/api/incidents/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        const incidents = res.data as Array<{ incident_type: string }>;
        setEventsToday(incidents.length);
        setActiveAlerts(incidents.filter(i => i.incident_type !== "normal").length);
        setCameras(12);
        setCoverageAreas(8);
      } catch (err: any) {
        console.error("Error fetching data:", err);
        if (err.response?.status === 401) {
          clearAuthData();
          router.push("/login");
        } else {
          setSystemStatus("Error");
        }
      }
    })();
  }, [token, router]);

  const handleLogout = () => {
    clearAuthData();
    router.push("/login");
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <Shield className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Smart Road Safety System
              </h1>
              <p className="text-sm text-gray-600">Administrator Dashboard</p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <Badge variant={systemStatus === "Active" ? "default" : "destructive"}>
              {systemStatus}
            </Badge>
            <Button variant="ghost" size="sm">
              <Bell className="h-4 w-4" />
              {activeAlerts > 0 && (
                <Badge
                  variant="destructive"
                  className="ml-1 h-5 w-5 rounded-full p-0 text-xs"
                >
                  {activeAlerts}
                </Badge>
              )}
            </Button>
            <Button variant="ghost" size="sm" onClick={handleLogout}>
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </header>

      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
          <Card>
            <CardContent className="p-6 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Cameras</p>
                <p className="text-3xl font-bold text-gray-900">{cameras}</p>
              </div>
              <CameraIcon className="h-8 w-8 text-blue-600" />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active Alerts</p>
                <p className="text-3xl font-bold text-red-600">{activeAlerts}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Events Today</p>
                <p className="text-3xl font-bold text-gray-900">{eventsToday}</p>
              </div>
              <Clock className="h-8 w-8 text-green-600" />
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-6 flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Coverage Areas</p>
                <p className="text-3xl font-bold text-gray-900">{coverageAreas}</p>
              </div>
              <MapPin className="h-8 w-8 text-purple-600" />
            </CardContent>
          </Card>
        </div>

        <Tabs defaultValue={defaultTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="detection">Live Detection</TabsTrigger>
            <TabsTrigger value="events">Event Records</TabsTrigger>
            <TabsTrigger value="alerts">Alert Management</TabsTrigger>
            <TabsTrigger value="settings">System Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="detection">
            <LiveDetection />
          </TabsContent>

          <TabsContent value="events">
            <EventRecords />
          </TabsContent>

          <TabsContent value="alerts">
            <AlertPanel />
          </TabsContent>

          <TabsContent value="settings">
            <SystemSettings />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
