"use client";

import React, { createContext, useContext, useEffect, useState, useCallback } from "react";
import { apiClient } from "@/lib/api";

export interface LocationInfo {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  timezone: string;
  elevation?: number;
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
  addAndSelectLocation: (loc: LocationInfo) => void;
}

const LocationContext = createContext<LocationContextType>({
  locationId: "kavali",
  setLocationId: () => {},
  locations: [],
  currentLocation: null,
  isLoading: true,
  refreshKey: 0,
  triggerRefresh: () => {},
  addAndSelectLocation: () => {},
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

  const fetchLocations = useCallback(async () => {
    try {
      const data = await apiClient<LocationInfo[]>("/api/v1/locations");
      if (Array.isArray(data) && data.length > 0) {
        setLocations(data);
      }
    } catch {
      setLocations((prev) =>
        prev.length > 0 ? prev : [{ id: "kavali", name: "Kavali", latitude: 15.4833, longitude: 79.9167, timezone: "Asia/Kolkata" }]
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchLocations();
  }, [fetchLocations, refreshKey]);

  const setLocationId = useCallback((id: string) => {
    setLocationIdState(id);
    localStorage.setItem("atmosiq-location", id);
    setRefreshKey((prev) => prev + 1);
  }, []);

  const triggerRefresh = useCallback(() => {
    setRefreshKey((prev) => prev + 1);
  }, []);

  const addAndSelectLocation = useCallback((newLoc: LocationInfo) => {
    setLocations((prev) => {
      const exists = prev.some((l) => l.id === newLoc.id);
      return exists ? prev : [newLoc, ...prev];
    });
    setLocationIdState(newLoc.id);
    localStorage.setItem("atmosiq-location", newLoc.id);
    setRefreshKey((prev) => prev + 1);
  }, []);

  const currentLocation = locations.find((l) => l.id === locationId) || (locations.length > 0 ? locations[0] : null);

  return (
    <LocationContext.Provider
      value={{ locationId, setLocationId, locations, currentLocation, isLoading, refreshKey, triggerRefresh, addAndSelectLocation }}
    >
      {children}
    </LocationContext.Provider>
  );
}

export function useLocation() {
  return useContext(LocationContext);
}
