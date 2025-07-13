'use client';

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import api from '@/lib/api'; // Correctly using the centralized api instance

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

// Corrected relative paths for components within the same directory
import LiveDetection from "./UnifiedDetection";
import EventRecords from "./event-records";
import AlertPanel from "./alert-panel";
import SystemSettings from "./system-settings";

import { getAuthToken, clearAuthData } from "@/lib/auth";

// Define a more specific type for the incident data we expect
interface IncidentData {
  incident_type: string;
  timestamp: string;
}

export default function DashboardPage() {
  const [activeAlerts, setActiveAlerts] = useState(0);
  const [eventsToday, setEventsToday] = useState(0);
  const [cameras] = useState(12); // Static value
  const [coverageAreas] = useState(8); // Static value
  const [systemStatus, setSystemStatus] = useState<"Active" | "Error">("Active");
  const [defaultTab] = useState<"detection">("detection");
  const router = useRouter();

  useEffect(() => {
    // This effect runs once on component mount to fetch initial data
    const token = getAuthToken();
    if (!token) {
      router.push("/login");
      return; // Stop execution if not authenticated
    }

    const fetchData = async () => {
      try {
        const res = await api.get<IncidentData[]>('/incidents/');
        const incidents = res.data;

        const today = new Date().toDateString();
        const todaysEvents = incidents.filter(i => new Date(i.timestamp).toDateString() === today);
        
        setEventsToday(todaysEvents.length);
        setActiveAlerts(incidents.filter(i => i.incident_type !== "normal").length);
        setSystemStatus("Active");

      } catch (err) {
        // The catch block is now much simpler.
        // Our api.ts interceptor handles 401 errors automatically.
        // This block will catch other errors, like network failures.
        console.error("Error fetching dashboard data:", err);
        setSystemStatus("Error");
      }
    };

    fetchData();
  }, [router]); // Dependency array ensures this runs once on load

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
                  className="ml-1 h-5 w-5 rounded-full p-0 text-xs flex items-center justify-center"
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
