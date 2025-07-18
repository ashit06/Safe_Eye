// src/components/dashboard.tsx

'use client';

import { useState, useEffect, useRef, useCallback } from "react";
import { useRouter } from "next/navigation";
import api from '@/lib/api';
import useSound from 'use-sound';

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

import LiveDetection from "./UnifiedDetection";
import EventRecords from "./event-records";
import AlertPanel from "./alert-panel";
import SystemSettings from "./system-settings";

import { getAuthToken, clearAuthData } from "@/lib/auth";

interface IncidentData {
  id: number;
  incident_type: string;
  timestamp: string;
  status: 'active' | 'resolved' | 'investigating';
}

interface SystemSettingsData {
    id: number;
    sound_alert_enabled: boolean;
}

export default function DashboardPage() {
  const [activeAlerts, setActiveAlerts] = useState(0);
  const [eventsToday, setEventsToday] = useState(0);
  const [cameras] = useState(12);
  const [coverageAreas] = useState(8);
  const [systemStatus, setSystemStatus] = useState<"Active" | "Error">("Active");
  
  const router = useRouter();
  const wsRef = useRef<WebSocket | null>(null);

  const [playAlertSound] = useSound('/sounds/alert-sound.mp3', { volume: 0.5 });

  // This function fetches all necessary data for the dashboard.
  // useCallback ensures it's not recreated on every render.
  const fetchDashboardData = useCallback(async () => {
    try {
      const incidentsRes = await api.get<IncidentData[]>('/incidents/');
      const incidents = incidentsRes.data;
      
      const active = incidents.filter(i => i.status === "active");
      setActiveAlerts(active.length);

      const today = new Date();
      today.setHours(0, 0, 0, 0);
      const todaysEvents = incidents.filter(i => new Date(i.timestamp) >= today);
      setEventsToday(todaysEvents.length);
      
      setSystemStatus("Active");

    } catch (err) {
      console.error("Error fetching dashboard data:", err);
      setSystemStatus("Error");
    }
  }, []); // Empty dependency array means this function is stable.

  // This effect runs only ONCE when the component mounts.
  useEffect(() => {
    const token = getAuthToken();
    if (!token) {
      router.push("/login");
      return;
    }

    // Fetch initial data for the dashboard counts.
    fetchDashboardData();

    // Fetch the system settings separately, as they are needed for the WebSocket.
    const fetchSettings = async () => {
        try {
            const settingsRes = await api.get<SystemSettingsData[]>('/settings/');
            return settingsRes.data[0] || null;
        } catch (error) {
            console.error("Failed to fetch settings", error);
            return null;
        }
    };

    // --- THIS IS THE FIX ---
    // The WebSocket setup is now inside an async function within the useEffect
    // to ensure settings are fetched BEFORE the onmessage handler is defined.
    const setupWebSocket = async () => {
        const currentSettings = await fetchSettings();

        const WEBSOCKET_URL = process.env.NEXT_PUBLIC_WEBSOCKET_URL || "ws://127.0.0.1:8000";
        wsRef.current = new WebSocket(`${WEBSOCKET_URL}/ws/notifications/`);

        wsRef.current.onopen = () => console.log("Dashboard WebSocket connected");
        wsRef.current.onclose = () => console.log("Dashboard WebSocket disconnected");
        
        wsRef.current.onmessage = (event) => {
          const data = JSON.parse(event.data);
          
          if (data.message_type === 'new_incident_alert') {
            console.log("New incident received, refreshing dashboard data...");
            // When a new incident arrives, re-fetch the data to update counts.
            fetchDashboardData();
            
            // Use the settings we fetched earlier to check if sound should play.
            if (currentSettings?.sound_alert_enabled) {
              playAlertSound();
            }
          }
        };
    };

    setupWebSocket();
    
    // The cleanup function will run when the component unmounts.
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
    // The dependency array is now correct, preventing the infinite loop.
  }, [router, fetchDashboardData, playAlertSound]);

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
        {/* KPI Cards */}
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

        {/* Main Content Tabs */}
        <Tabs defaultValue="detection" className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="detection">Live Detection</TabsTrigger>
            <TabsTrigger value="events">Event Records</TabsTrigger>
            <TabsTrigger value="alerts">Alert Management</TabsTrigger>
            <TabsTrigger value="settings">System Settings</TabsTrigger>
          </TabsList>

          <TabsContent value="detection"><LiveDetection /></TabsContent>
          <TabsContent value="events"><EventRecords /></TabsContent>
          {/* Pass the WebSocket ref to the AlertPanel so it can listen for new alerts */}
          <TabsContent value="alerts"><AlertPanel wsRef={wsRef} /></TabsContent>
          <TabsContent value="settings"><SystemSettings /></TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
