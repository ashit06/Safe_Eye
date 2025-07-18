// src/components/alert-panel.tsx

"use client";

import { useState, useEffect, RefObject } from "react";
import api from '@/lib/api';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Bell, Mail, Loader2, Save } from "lucide-react";

interface Incident {
  id: number;
  incident_type: string;
  location: string;
  timestamp: string;
  status: 'active' | 'investigating' | 'resolved';
}

interface SystemSettings {
    id: number;
    email_alert_enabled: boolean;
    sound_alert_enabled: boolean;
    alert_email_address: string;
    email_alert_template: string;
}

// The component now accepts the WebSocket reference as a prop
interface AlertPanelProps {
  wsRef: RefObject<WebSocket | null>;
}

export default function AlertPanel({ wsRef }: AlertPanelProps) {
  const [alerts, setAlerts] = useState<Incident[]>([]);
  const [settings, setSettings] = useState<Partial<SystemSettings>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    // Fetch the initial list of active alerts when the component loads
    const fetchInitialData = async () => {
      setIsLoading(true);
      try {
        const [alertsRes, settingsRes] = await Promise.all([
          api.get<Incident[]>('/incidents/?status=active'),
          api.get<SystemSettings[]>('/settings/')
        ]);
        
        setSettings(settingsRes.data[0] || {});
        setAlerts(alertsRes.data);
      } catch (err) {
        console.error("Failed to fetch initial data", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchInitialData();

    // Listen for new messages on the WebSocket passed from the dashboard
    const handleWebSocketMessage = (event: MessageEvent) => {
        const data = JSON.parse(event.data);
        // Check for the specific message type from the backend signal
        if (data.message_type === 'new_incident_alert' && data.incident) {
            // Add the new incident to the top of the alerts list to update the UI
            setAlerts(prevAlerts => [data.incident, ...prevAlerts]);
        }
    };

    const ws = wsRef.current;
    if (ws) {
        ws.addEventListener('message', handleWebSocketMessage);
    }

    // Cleanup function to remove the event listener when the component unmounts
    return () => {
        if (ws) {
            ws.removeEventListener('message', handleWebSocketMessage);
        }
    };
  }, [wsRef]); // This effect depends on the WebSocket reference

  const handleSettingChange = (key: keyof SystemSettings, value: any) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSaveChanges = async () => {
    if (!settings.id) return;
    setIsSaving(true);
    try {
      await api.patch(`/settings/${settings.id}/`, settings);
      console.log("Settings saved successfully!");
    } catch (err) {
      console.error("Failed to save settings", err);
    } finally {
      setIsSaving(false);
    }
  };
  
  const acknowledgeAlert = async (incidentId: number) => {
    try {
      await api.patch(`/incidents/${incidentId}/`, { status: "resolved" });
      setAlerts((prev) => prev.filter((alert) => alert.id !== incidentId));
    } catch (err) {
      console.error("Failed to acknowledge alert", err);
    }
  };

  if (isLoading) {
    return (
        <div className="flex justify-center items-center p-8">
            <Loader2 className="h-8 w-8 animate-spin" />
        </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-red-500" />
            Active Alerts
          </CardTitle>
          <CardDescription>Current alerts requiring attention</CardDescription>
        </CardHeader>
        <CardContent>
          {alerts.length === 0 ? (
            <p className="text-center text-gray-500">No active alerts at this moment.</p>
          ) : (
            <div className="space-y-4">
              {alerts.map((alert) => (
                <div key={alert.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div>
                    <h4 className="font-medium capitalize">{alert.incident_type}</h4>
                    <p className="text-sm text-gray-600">{alert.location}</p>
                     <p className="text-xs text-gray-400">
                      {new Date(alert.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <Button size="sm" variant="outline" onClick={() => acknowledgeAlert(alert.id)}>
                    Acknowledge
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Settings Section (unchanged) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Notification Settings</CardTitle>
            <CardDescription>Configure how you receive alerts</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4" />
                <Label htmlFor="email-notifications">Email Notifications</Label>
              </div>
              <Switch
                id="email-notifications"
                checked={settings.email_alert_enabled ?? false}
                onCheckedChange={(checked) => handleSettingChange('email_alert_enabled', checked)}
              />
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bell className="h-4 w-4" />
                <Label htmlFor="sound-alerts">Sound Alerts (Dashboard)</Label>
              </div>
              <Switch
                id="sound-alerts"
                checked={settings.sound_alert_enabled ?? false}
                onCheckedChange={(checked) => handleSettingChange('sound_alert_enabled', checked)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="alert-email">Alert Email Address</Label>
              <Input
                id="alert-email"
                type="email"
                value={settings.alert_email_address || ''}
                onChange={(e) => handleSettingChange('alert_email_address', e.target.value)}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Email Message Template</CardTitle>
            <CardDescription>Customize the alert message format</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email-template">
                Placeholders: {"{incident_type}"}, {"{location}"}, {"{timestamp}"}, {"{confidence}"}
              </Label>
              <Textarea
                id="email-template"
                value={settings.email_alert_template || ''}
                onChange={(e) => handleSettingChange('email_alert_template', e.target.value)}
                rows={8}
              />
            </div>
          </CardContent>
        </Card>
      </div>
      
      <div className="flex justify-end">
        <Button onClick={handleSaveChanges} disabled={isSaving}>
          {isSaving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
          Save All Settings
        </Button>
      </div>
    </div>
  );
}
