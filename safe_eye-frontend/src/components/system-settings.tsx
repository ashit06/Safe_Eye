"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Switch } from "@/components/ui/switch"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Slider } from "@/components/ui/slider"
import { Badge } from "@/components/ui/badge"
import { Settings, Camera, Shield, Database, Wifi } from "lucide-react"

export default function SystemSettings() {
  const [detectionSensitivity, setDetectionSensitivity] = useState([75])
  const [autoRecording, setAutoRecording] = useState(true)
  const [nightVision, setNightVision] = useState(true)
  const [motionDetection, setMotionDetection] = useState(true)

  return (
    <div className="space-y-6">
      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            System Status
          </CardTitle>
          <CardDescription>Current system health and performance</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Camera className="h-8 w-8 text-green-500" />
              </div>
              <p className="text-sm font-medium">Camera System</p>
              <Badge variant="default">Online</Badge>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Database className="h-8 w-8 text-green-500" />
              </div>
              <p className="text-sm font-medium">Database</p>
              <Badge variant="default">Connected</Badge>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Wifi className="h-8 w-8 text-green-500" />
              </div>
              <p className="text-sm font-medium">Network</p>
              <Badge variant="default">Stable</Badge>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center mb-2">
                <Settings className="h-8 w-8 text-green-500" />
              </div>
              <p className="text-sm font-medium">AI Detection</p>
              <Badge variant="default">Active</Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Detection Settings */}
        <Card>
          <CardHeader>
            <CardTitle>Detection Settings</CardTitle>
            <CardDescription>Configure AI detection parameters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label>Detection Sensitivity: {detectionSensitivity[0]}%</Label>
              <Slider
                value={detectionSensitivity}
                onValueChange={setDetectionSensitivity}
                max={100}
                min={10}
                step={5}
                className="w-full"
              />
              <p className="text-xs text-gray-500">Higher sensitivity may result in more false positives</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="detection-model">AI Detection Model</Label>
              <Select defaultValue="advanced">
                <SelectTrigger>
                  <SelectValue placeholder="Select model" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="basic">Basic Detection</SelectItem>
                  <SelectItem value="standard">Standard Detection</SelectItem>
                  <SelectItem value="advanced">Advanced Detection</SelectItem>
                  <SelectItem value="premium">Premium Detection</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="motion-detection">Motion Detection</Label>
                <Switch id="motion-detection" checked={motionDetection} onCheckedChange={setMotionDetection} />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="night-vision">Night Vision Mode</Label>
                <Switch id="night-vision" checked={nightVision} onCheckedChange={setNightVision} />
              </div>

              <div className="flex items-center justify-between">
                <Label htmlFor="auto-recording">Auto Recording</Label>
                <Switch id="auto-recording" checked={autoRecording} onCheckedChange={setAutoRecording} />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Camera Configuration */}
        <Card>
          <CardHeader>
            <CardTitle>Camera Configuration</CardTitle>
            <CardDescription>Manage camera settings and zones</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="recording-quality">Recording Quality</Label>
              <Select defaultValue="1080p">
                <SelectTrigger>
                  <SelectValue placeholder="Select quality" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="720p">720p HD</SelectItem>
                  <SelectItem value="1080p">1080p Full HD</SelectItem>
                  <SelectItem value="4k">4K Ultra HD</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="frame-rate">Frame Rate (FPS)</Label>
              <Select defaultValue="30">
                <SelectTrigger>
                  <SelectValue placeholder="Select frame rate" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="15">15 FPS</SelectItem>
                  <SelectItem value="24">24 FPS</SelectItem>
                  <SelectItem value="30">30 FPS</SelectItem>
                  <SelectItem value="60">60 FPS</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="storage-duration">Storage Duration</Label>
              <Select defaultValue="30">
                <SelectTrigger>
                  <SelectValue placeholder="Select duration" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="7">7 Days</SelectItem>
                  <SelectItem value="14">14 Days</SelectItem>
                  <SelectItem value="30">30 Days</SelectItem>
                  <SelectItem value="90">90 Days</SelectItem>
                  <SelectItem value="365">1 Year</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button className="w-full" variant="outline">
              Configure Camera Zones
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Database Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Database & Storage</CardTitle>
          <CardDescription>Manage data storage and backup settings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center p-4 border rounded-lg">
              <p className="text-2xl font-bold text-blue-600">2.4 TB</p>
              <p className="text-sm text-gray-600">Total Storage</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <p className="text-2xl font-bold text-green-600">1.8 TB</p>
              <p className="text-sm text-gray-600">Used Storage</p>
            </div>
            <div className="text-center p-4 border rounded-lg">
              <p className="text-2xl font-bold text-orange-600">0.6 TB</p>
              <p className="text-sm text-gray-600">Available</p>
            </div>
          </div>

          <div className="flex gap-4">
            <Button variant="outline">
              <Database className="h-4 w-4 mr-2" />
              Backup Database
            </Button>
            <Button variant="outline">Clean Old Records</Button>
            <Button variant="outline">Export Data</Button>
          </div>
        </CardContent>
      </Card>

      {/* Save Settings */}
      <div className="flex justify-end">
        <Button size="lg">Save All Settings</Button>
      </div>
    </div>
  )
}
