"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { apiClient } from "@/lib/api";

export interface LocationInfo {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  timezone: string;
  state?: string;
  country?: string;
}

interface LocationContextType {
  locationId: string;
  setLocationId: (id: string) => void;
  locations: LocationInfo[];
  currentLocation: LocationInfo | null;
  isLoading: boolean;
  refreshKey: number;
  triggerRefresh: () => void;
}

const LocationContext = createContext<LocationContextType>({
  locationId: "kavali",
  setLocationId: () => {},
  locations: [],
  currentLocation: null,
  isLoading: true,
  refreshKey: 0,
  triggerRefresh: () => {},
});

export function LocationProvider({ children }: { children: React.ReactNode }) {
  const [locationId, setLocationIdState] = useState("kavali");
  const [locations, setLocations] = useState<LocationInfo[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    const stored = localStorage.getItem("atmosiq-location");
    if (stored) {
      setLocationIdState(stored);
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function fetchLocations() {
      try {
        const data = await apiClient<LocationInfo[]>("/api/v1/locations");
        if (!cancelled && Array.isArray(data) && data.length > 0) {
          setLocations(data);
        }
      } catch {
        // Use minimal fallback only if API is completely unreachable
        if (!cancelled) {
          setLocations([
            { id: "kavali", name: "Kavali", latitude: 15.4833, longitude: 79.9167, timezone: "Asia/Kolkata" },
          ]);
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }
    fetchLocations();
    return () => { cancelled = true; };
  }, []);

  const setLocationId = useCallback((id: string) => {
    setLocationIdState(id);
    localStorage.setItem("atmosiq-location", id);
  }, []);

  const triggerRefresh = useCallback(() => {
    setRefreshKey((prev) => prev + 1);
  }, []);

  const currentLocation = locations.find((l) => l.id === locationId) || null;

  return (
    <LocationContext.Provider
      value={{ locationId, setLocationId, locations, currentLocation, isLoading, refreshKey, triggerRefresh }}
    >
      {children}
    </LocationContext.Provider>
  );
}

export function useLocation() {
  return useContext(LocationContext);
}
