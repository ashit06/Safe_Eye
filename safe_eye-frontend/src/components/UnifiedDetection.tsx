'use client';

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Upload, Loader2, Camera } from "lucide-react";

interface Detection {
  label: string;
  confidence: number;
}

export default function UnifiedDetection() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const [wsConnected, setWsConnected] = useState(false);
  const [wsError, setWsError] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const captureIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "ws://127.0.0.1:8000/ws/detect/";

  const startWebSocket = () => {
    setWsError(null);
    wsRef.current = new WebSocket(API_BASE);
    
    wsRef.current.onopen = () => {
      console.log("WebSocket connected");
      setWsConnected(true);
      startCamera();
    };

    wsRef.current.onerror = () => {
      console.error("WebSocket error");
      setWsError("WebSocket connection failed.");
      wsRef.current?.close();
    };

    wsRef.current.onclose = () => {
      console.log("WebSocket closed");
      setWsConnected(false);
      stopCamera();
    };

    // 🔥 Here is the important update for receiving detection data
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "detections") {
          setDetections(data.detections || []);
        } else if (data.type === "connection_established" || data.type === "status") {
          console.log(data.message);
        }
      } catch (err) {
        console.error("Invalid message format", err);
      }
    };
  };

  const stopWebSocket = () => {
    wsRef.current?.close();
    setWsConnected(false);
    stopCamera();
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();

        captureIntervalRef.current = setInterval(() => {
          sendFrame();
        }, 500); // capture every 500ms
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
    }
  };

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    if (captureIntervalRef.current) {
      clearInterval(captureIntervalRef.current);
    }
  };

  const sendFrame = () => {
    if (!videoRef.current || !canvasRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      console.log("Skipping frame send, something not ready");
      return;
    }

    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);
    
    canvasRef.current.toBlob((blob) => {
      if (blob) {
        blob.arrayBuffer().then(buffer => {
          wsRef.current?.send(buffer);
          console.log("Frame sent");
        });
      }
    }, 'image/jpeg', 0.7);
  };

  useEffect(() => {
    return () => {
      stopWebSocket();
    };
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setSelectedFile(file);
    setPreviewUrl(file ? URL.createObjectURL(file) : null);
    setDetections([]);
  };

  const handleManualDetect = async () => {
    if (!selectedFile) return;
    setIsLoading(true);
    setDetections([]);

    const formData = new FormData();
    formData.append("image", selectedFile);

    try {
      const res = await fetch("http://127.0.0.1:8000/api/ai/incident/", {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        setDetections(data.detections || []);
      } else {
        console.error("Manual detect error", res.statusText);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Unified AI Detection</CardTitle>
          <CardDescription>Stream live video or upload image for AI analysis.</CardDescription>
        </CardHeader>
        <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Live WebSocket Stream */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Live Stream</h3>
            <div className="mb-4 flex items-center gap-4">
              <Button onClick={wsConnected ? stopWebSocket : startWebSocket}>
                {wsConnected ? "Stop Stream" : "Start Stream"}
              </Button>
              <Badge variant={wsConnected ? "default" : "secondary"}>
                {wsConnected ? "🟢 Connected" : "⚪ Disconnected"}
              </Badge>
            </div>
            {wsError && <p className="text-red-500">{wsError}</p>}
            <div className="aspect-video bg-gray-900 rounded-lg flex items-center justify-center overflow-hidden">
              <video ref={videoRef} autoPlay muted className="w-full h-full object-cover" />
              <canvas ref={canvasRef} width="640" height="480" style={{ display: 'none' }} />
            </div>
          </div>

          {/* Manual Detection */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Manual Detection</h3>
            <div className="flex items-center gap-4 mb-4">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                disabled={isLoading}
                className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
              />
              <Button onClick={handleManualDetect} disabled={!selectedFile || isLoading}>
                {isLoading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Upload className="h-4 w-4 mr-2" />}
                Detect
              </Button>
            </div>
            <div className="aspect-video bg-gray-100 rounded-lg flex items-center justify-center">
              {previewUrl ? (
                <img src={previewUrl} alt="Preview" className="w-full h-full object-contain" />
              ) : (
                <div className="text-gray-400 text-center">
                  <Upload className="h-12 w-12 mx-auto mb-2" />
                  <p>Upload an image to see results</p>
                </div>
              )}
            </div>
            {detections.length > 0 && (
              <div className="mt-4">
                <h3 className="font-bold">Detections:</h3>
                <ul className="list-disc list-inside">
                  {detections.map((det, i) => (
                    <li key={i}>{det.label} ({(det.confidence * 100).toFixed(1)}%)</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
