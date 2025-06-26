"use client";

import { useState, useEffect } from "react";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Bell, Mail, Phone, MessageSquare } from "lucide-react";
import { getAuthToken } from "@/lib/auth";

interface Incident {
  id: number;
  incident_type: string;
  description: string;
  location: string;
  timestamp: string;
  reported_by: number;
}

export default function AlertPanel() {
  const [alerts, setAlerts] = useState<Incident[]>([]);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [smsNotifications, setSmsNotifications] = useState(false);
  const [soundAlerts, setSoundAlerts] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    const token = getAuthToken();
    if (!token) return;

    setIsLoading(true);
    try {
      const response = await axios.get("http://127.0.0.1:8000/api/incidents/", {
        headers: { Authorization: `Bearer ${token}` },
      });

      // Filter out normal incidents (only show active ones)
      const activeAlerts = response.data.filter(
        (incident: Incident) => incident.incident_type.toLowerCase() !== "normal"
      );
      setAlerts(activeAlerts);
    } catch (err) {
      console.error("Failed to fetch alerts", err);
    } finally {
      setIsLoading(false);
    }
  };

  const acknowledgeAlert = async (incidentId: number) => {
    const token = getAuthToken();
    if (!token) return;

    try {
      await axios.patch(
        `http://127.0.0.1:8000/api/incidents/${incidentId}/`,
        { status: "resolved" }, // You may need to adjust this field according to your backend schema
        { headers: { Authorization: `Bearer ${token}` } }
      );
      // Remove acknowledged alert from UI
      setAlerts((prev) => prev.filter((alert) => alert.id !== incidentId));
    } catch (err) {
      console.error("Failed to acknowledge alert", err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Active Alerts */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5 text-red-500" />
            Active Alerts
          </CardTitle>
          <CardDescription>Current alerts requiring attention</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <p>Loading alerts...</p>
          ) : alerts.length === 0 ? (
            <p className="text-center text-gray-500">No active alerts at this moment.</p>
          ) : (
            <div className="space-y-4">
              {alerts.map((alert) => (
                <div key={alert.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium capitalize">{alert.incident_type}</h4>
                      <Badge
                        variant={
                          ["murder", "robbery", "accident"].includes(alert.incident_type.toLowerCase())
                            ? "destructive"
                            : "default"
                        }
                      >
                        {alert.incident_type}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600">{alert.location}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(alert.timestamp).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="destructive">Active</Badge>
                    <Button size="sm" variant="outline" onClick={() => acknowledgeAlert(alert.id)}>
                      Acknowledge
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Notification Settings */}
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
              <Switch id="email-notifications" checked={emailNotifications} onCheckedChange={setEmailNotifications} />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4" />
                <Label htmlFor="sms-notifications">SMS Notifications</Label>
              </div>
              <Switch id="sms-notifications" checked={smsNotifications} onCheckedChange={setSmsNotifications} />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bell className="h-4 w-4" />
                <Label htmlFor="sound-alerts">Sound Alerts</Label>
              </div>
              <Switch id="sound-alerts" checked={soundAlerts} onCheckedChange={setSoundAlerts} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="alert-email">Alert Email Address</Label>
              <Input id="alert-email" type="email" placeholder="admin@roadsafety.com" defaultValue="admin@roadsafety.com" />
            </div>

            <div className="space-y-2">
              <Label htmlFor="alert-phone">Alert Phone Number</Label>
              <Input id="alert-phone" type="tel" placeholder="+1-555-0123" defaultValue="+1-555-0123" />
            </div>
          </CardContent>
        </Card>

        {/* Emergency Contacts */}
        <Card>
          <CardHeader>
            <CardTitle>Emergency Contacts</CardTitle>
            <CardDescription>Configured notification recipients</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-3 border rounded-lg">
                <h4 className="font-medium">Police Department</h4>
                <div className="text-sm text-gray-600">
                  <Mail className="h-3 w-3 inline" /> police@city.gov <br />
                  <Phone className="h-3 w-3 inline" /> +1-911
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Alert Template */}
      <Card>
        <CardHeader>
          <CardTitle>Alert Message Template</CardTitle>
          <CardDescription>Customize the alert message format</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email-template">Email Template</Label>
              <Textarea
                id="email-template"
                placeholder="Alert: {EVENT_TYPE} detected at {LOCATION}..."
                defaultValue="URGENT ALERT: {EVENT_TYPE} detected at {LOCATION} on {DATE} at {TIME}. Severity Level: {SEVERITY}. Immediate response required."
                rows={4}
              />
            </div>
            <Button>Save Template</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
