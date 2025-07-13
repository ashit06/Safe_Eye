'use client';

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Upload, Loader2, Video, VideoOff } from "lucide-react";
import api from '@/lib/api'; // Use the centralized api instance

interface Detection {
  label: string;
  confidence: number;
}

export default function UnifiedDetection() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [wsError, setWsError] = useState<string | null>(null);

  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const captureIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Use the dedicated WebSocket URL from environment variables
  const WEBSOCKET_URL = process.env.NEXT_PUBLIC_WEBSOCKET_URL || "ws://127.0.0.1:8000";

  const startWebSocket = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) return;
    
    setWsError(null);
    // Append the correct path to the base WebSocket URL
    wsRef.current = new WebSocket(`${WEBSOCKET_URL}/ws/detect/`);
    
    wsRef.current.onopen = () => {
      console.log("WebSocket connected");
      setIsStreaming(true);
      startCamera();
    };

    wsRef.current.onerror = (event) => {
      console.error("WebSocket error:", event);
      setWsError("WebSocket connection failed. Please check the server and your connection.");
      setIsStreaming(false);
    };

    wsRef.current.onclose = () => {
      console.log("WebSocket closed");
      setIsStreaming(false);
      stopCamera();
    };

    // FIX 1: The backend sends 'predictions', not 'detections'.
    wsRef.current.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === "detections") {
          setDetections(data.predictions || []); // This line is now fixed
        }
      } catch (err) {
        console.error("Invalid message format from WebSocket", err);
      }
    };
  };

  const stopWebSocket = () => {
    wsRef.current?.close();
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
        // Start sending frames after a short delay
        setTimeout(() => {
            captureIntervalRef.current = setInterval(sendFrame, 500); // Send frame every 500ms
        }, 500);
      }
    } catch (err) {
      console.error("Error accessing camera:", err);
      setWsError("Could not access camera. Please grant permission.");
      stopWebSocket();
    }
  };

  const stopCamera = () => {
    if (captureIntervalRef.current) {
      clearInterval(captureIntervalRef.current);
      captureIntervalRef.current = null;
    }
    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
  };

  // FIX 2: The backend expects a JSON object with a base64 image string.
  const sendFrame = () => {
    if (!videoRef.current || !canvasRef.current || wsRef.current?.readyState !== WebSocket.OPEN) {
      return;
    }
    const context = canvasRef.current.getContext('2d');
    if (context) {
      context.drawImage(videoRef.current, 0, 0, 640, 480);
      const dataUrl = canvasRef.current.toDataURL('image/jpeg');
      wsRef.current.send(JSON.stringify({ image: dataUrl }));
    }
  };

  useEffect(() => {
    // Cleanup function to close WebSocket and camera when component unmounts
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

  // FIX 3: This function now uses the central 'api' instance instead of fetch.
  const handleManualDetect = async () => {
    if (!selectedFile) return;
    setIsLoading(true);
    setDetections([]);

    const formData = new FormData();
    formData.append("image", selectedFile);

    try {
      const res = await api.post('/ai/incident/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setDetections(res.data.detections || []);
    } catch (err) {
      console.error("Manual detection error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Unified AI Detection</CardTitle>
        <CardDescription>Stream live video or upload an image for AI analysis.</CardDescription>
      </CardHeader>
      <CardContent className="grid md:grid-cols-2 gap-6">
        {/* Live Stream Section */}
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">Live Stream</h3>
          <div className="flex items-center gap-4">
            <Button onClick={isStreaming ? stopWebSocket : startWebSocket}>
              {isStreaming ? <VideoOff className="mr-2 h-4 w-4" /> : <Video className="mr-2 h-4 w-4" />}
              {isStreaming ? "Stop Stream" : "Start Stream"}
            </Button>
            <Badge variant={isStreaming ? "default" : "secondary"}>
              {isStreaming ? "● Live" : "Offline"}
            </Badge>
          </div>
          {wsError && <p className="text-sm text-red-600">{wsError}</p>}
          <div className="aspect-video bg-slate-900 rounded-lg overflow-hidden relative">
            <video ref={videoRef} playsInline autoPlay muted className="w-full h-full object-cover" />
            <canvas ref={canvasRef} width="640" height="480" className="hidden" />
            {!isStreaming && (
              <div className="absolute inset-0 flex items-center justify-center text-slate-400">
                <p>Camera is off</p>
              </div>
            )}
          </div>
        </div>
        
        {/* Manual Upload Section */}
        <div className="space-y-4">
          <h3 className="font-semibold text-lg">Manual Detection</h3>
          <div className="flex items-center gap-4">
            <Input type="file" accept="image/*" onChange={handleFileChange} disabled={isLoading} />
            <Button onClick={handleManualDetect} disabled={!selectedFile || isLoading}>
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Upload className="mr-2 h-4 w-4" />}
              Detect
            </Button>
          </div>
          <div className="aspect-video bg-slate-100 rounded-lg flex items-center justify-center">
            {previewUrl ? (
              <img src={previewUrl} alt="Upload preview" className="max-h-full max-w-full object-contain" />
            ) : (
              <div className="text-center text-slate-500">
                <Upload className="mx-auto h-10 w-10 mb-2" />
                <p>Upload an image to analyze</p>
              </div>
            )}
          </div>
        </div>
      </CardContent>
      {detections.length > 0 && (
        <CardContent>
            <h3 className="font-bold text-lg mb-2">Detection Results:</h3>
            <div className="flex flex-wrap gap-2">
            {detections.map((det, i) => (
                <Badge key={i} variant="destructive" className="text-base">
                {det.label} ({(det.confidence * 100).toFixed(1)}%)
                </Badge>
            ))}
            </div>
        </CardContent>
        )}
    </Card>
  );
}
