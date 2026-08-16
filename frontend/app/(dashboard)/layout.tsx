"use client";

import React from "react";
import { Sidebar } from "@/components/layout/sidebar";
import { Topbar } from "@/components/layout/topbar";
import { LocationProvider } from "@/lib/location-context";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <LocationProvider>
      <div className="min-h-screen flex" style={{ background: "var(--background)", color: "var(--foreground)" }}>
        {/* Collapsible Left Sidebar */}
        <Sidebar />

        {/* Main Container */}
        <div className="flex-1 flex flex-col min-w-0 overflow-x-hidden">
          <Topbar />
          <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-[1440px] mx-auto w-full">
            {children}
          </main>
        </div>
      </div>
    </LocationProvider>
  );
}
