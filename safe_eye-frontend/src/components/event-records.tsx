'use client';

import { useState, useEffect } from "react";
import axios from "axios";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, Download, Eye, AlertTriangle, Loader2 } from "lucide-react";

import { getAuthToken, clearAuthData } from "@/lib/auth";

interface Incident {
  id: number;
  incident_type: string;
  description: string;
  location: string;
  timestamp: string;
  reported_by: number;
}

export default function EventRecords() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState("all");
  const router = useRouter();
  const token = getAuthToken();

  // Fetch incidents on mount
  useEffect(() => {
    if (!token) {
      clearAuthData();
      router.push("/login");
      return;
    }
    (async () => {
      try {
        const res = await axios.get<Incident[]>(
          "http://127.0.0.1:8000/api/incidents/",
          { headers: { Authorization: `Bearer ${token}` } }
        );
        setIncidents(res.data);
      } catch (err: any) {
        console.error("Error fetching incidents:", err);
        if (err.response?.status === 401) {
          clearAuthData();
          router.push("/login");
        }
      } finally {
        setLoading(false);
      }
    })();
  }, [router, token]);

  // Filter & search
  const filtered = incidents.filter((inc) => {
    const matchesSearch =
      inc.id.toString().includes(searchTerm) ||
      inc.incident_type.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inc.location.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter =
      filterType === "all" ||
      inc.incident_type.toLowerCase() === filterType.toLowerCase();
    return matchesSearch && matchesFilter;
  });

  const badgeColor = (type: string) =>
    type === "accident" ? "destructive" : "default";

  if (loading) {
    return (
      <div className="p-6 text-center">
        <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
        <p>Loading events…</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Event Records</CardTitle>
          <CardDescription>
            Complete history of all detected incidents
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input
                placeholder="Search by ID, type, or location…"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-full sm:w-48">
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="accident">Accident</SelectItem>
                <SelectItem value="robbery">Robbery</SelectItem>
                <SelectItem value="murder">Murder</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
          </div>

          {/* Events Table */}
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>ID</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Location</TableHead>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filtered.map((inc) => (
                  <TableRow key={inc.id}>
                    <TableCell className="font-medium">{inc.id}</TableCell>
                    <TableCell>
                      <Badge variant={badgeColor(inc.incident_type) as any}>
                        {inc.incident_type}
                      </Badge>
                    </TableCell>
                    <TableCell>{inc.location}</TableCell>
                    <TableCell>
                      {new Date(inc.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
                {filtered.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center py-4">
                      No events match your criteria.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
