"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import {
  CloudSun, Sparkles, ArrowRight, ShieldCheck, Zap, Activity, Layers,
  BarChart3, Cpu, Droplets, Wind, Search, CheckCircle2, Gauge, Lock,
  Globe, Server, Database, LineChart as ChartIcon, Terminal, Moon, Sun,
  TrendingUp, Award, Radar, Eye, ArrowUpRight, Compass, Radio
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { WeatherIcon } from "@/components/ui/weather-icon";
import { useTheme } from "@/lib/theme-context";

export default function LandingPage() {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === "dark";
  const [searchLocation, setSearchLocation] = useState("Kavali, Andhra Pradesh");
  const [activeTab, setActiveTab] = useState<"forecast" | "mlops" | "models" | "drift">("forecast");

  const quickStations = ["Kavali", "Tirupati", "Nellore", "Vijayawada", "Hyderabad", "Bengaluru", "Chennai", "Delhi"];

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--foreground)] selection:bg-sky-500 selection:text-white font-sans transition-colors duration-300">
      {/* 1. Sticky Glassmorphism Header */}
      <header className="sticky top-0 z-50 w-full bg-[var(--card)]/80 backdrop-blur-xl border-b border-[var(--border)] transition-all">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-sky-400 via-blue-600 to-indigo-700 flex items-center justify-center text-white shadow-lg shadow-sky-500/25">
              <CloudSun size={22} className="text-white" />
            </div>
            <span className="text-xl font-extrabold tracking-tight font-sans">
              Atmos<span className="text-sky-500">IQ</span>
            </span>
          </Link>

          <nav className="hidden lg:flex items-center gap-8 text-xs font-semibold text-[var(--muted-foreground)]">
            <a href="#features" className="hover:text-sky-500 transition-colors">Weather Intelligence</a>
            <a href="#architecture" className="hover:text-sky-500 transition-colors">MLOps Architecture</a>
            <a href="#models" className="hover:text-sky-500 transition-colors">Model Arena</a>
            <a href="#benchmarks" className="hover:text-sky-500 transition-colors">Benchmarks</a>
            <Link href="/weather/map" className="hover:text-sky-500 transition-colors">Radar Map</Link>
            <a href="http://127.0.0.1:8001/docs" target="_blank" className="hover:text-sky-500 transition-colors">API Docs</a>
          </nav>

          <div className="flex items-center gap-3">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl border hover:bg-black/5 dark:hover:bg-white/5 transition-colors cursor-pointer"
              style={{ borderColor: "var(--border)", color: "var(--foreground)" }}
              title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
            >
              {isDark ? <Sun size={16} className="text-amber-400" /> : <Moon size={16} className="text-slate-700" />}
            </button>

            <Link href="/dashboard">
              <Button size="sm" className="bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold px-4 rounded-xl shadow-md shadow-blue-500/20">
                Launch Platform <ArrowRight size={14} className="ml-1" />
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* 2. Hero Section */}
      <section className="relative pt-16 pb-24 overflow-hidden border-b" style={{ borderColor: "var(--border)" }}>
        {/* Background Atmospheric Glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[500px] bg-gradient-to-tr from-sky-500/15 via-blue-600/20 to-purple-600/15 rounded-full blur-3xl pointer-events-none -z-10" />

        <div className="max-w-7xl mx-auto px-6 flex flex-col items-center text-center">
          {/* Top Status Pill */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-500/10 border border-blue-500/30 text-blue-600 dark:text-sky-400 text-xs font-bold mb-6 animate-pulse">
            <Radio size={14} className="text-blue-500" />
            <span>AtmosIQ 2.0 • Enterprise Meteorological Intelligence & Precision Climate Risk</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight max-w-5xl leading-[1.1] font-sans">
            AI-Powered Weather Intelligence <br className="hidden sm:block" />
            <span className="bg-gradient-to-r from-sky-500 via-blue-600 to-indigo-600 dark:from-sky-400 dark:via-blue-300 dark:to-indigo-200 bg-clip-text text-transparent">
              & Climate Risk Platform
            </span>
          </h1>

          <p className="mt-6 text-base sm:text-lg max-w-3xl leading-relaxed" style={{ color: "var(--muted-foreground)" }}>
            Empowering agriculture, renewable energy grids, logistics, and infrastructure with hyper-accurate, multi-horizon AI forecasts. 
            Anticipate severe storms, optimize energy dispatch, protect supply chains, and eliminate climate uncertainty with calibrated probabilistic intelligence.
          </p>

          {/* Search Bar / Location Input */}
          <div className="mt-8 w-full max-w-xl p-2 rounded-2xl border shadow-2xl backdrop-blur-xl flex flex-col sm:flex-row items-center gap-2" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
            <div className="flex items-center gap-2 flex-1 px-3 w-full">
              <Search size={18} className="text-blue-500" />
              <input
                type="text"
                value={searchLocation}
                onChange={(e) => setSearchLocation(e.target.value)}
                placeholder="Search station or city (e.g. Kavali, Tirupati, Hyderabad)..."
                className="bg-transparent flex-1 text-sm placeholder-slate-400 focus:outline-none py-1.5 font-medium"
                style={{ color: "var(--foreground)" }}
              />
            </div>
            <Link href="/dashboard" className="w-full sm:w-auto">
              <Button size="sm" className="w-full bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold px-5 py-2">
                Explore Station
              </Button>
            </Link>
          </div>

          {/* Quick Station Badges */}
          <div className="mt-4 flex flex-wrap items-center justify-center gap-2 text-xs">
            <span className="font-semibold text-[11px]" style={{ color: "var(--muted-foreground)" }}>Popular Stations:</span>
            {quickStations.map((st) => (
              <button
                key={st}
                onClick={() => setSearchLocation(`${st}, India`)}
                className="px-2.5 py-1 rounded-lg border text-[11px] font-semibold hover:border-blue-500 hover:text-blue-500 transition-colors cursor-pointer"
                style={{ background: "var(--muted)", borderColor: "var(--border)", color: "var(--foreground)" }}
              >
                {st}
              </button>
            ))}
          </div>

          {/* Hero Action Buttons */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link href="/dashboard">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-500 text-white text-sm font-bold px-6 rounded-xl shadow-lg shadow-blue-500/25">
                Explore Live Overview <ArrowRight size={16} className="ml-1.5" />
              </Button>
            </Link>
            <Link href="/forecast/comparison">
              <Button variant="secondary" size="lg" className="border text-sm font-bold px-6 rounded-xl" style={{ background: "var(--card)", borderColor: "var(--border)", color: "var(--foreground)" }}>
                View AI Forecast Comparison
              </Button>
            </Link>
          </div>

          {/* 3. Hero Visual Display Card */}
          <div className="mt-14 w-full max-w-5xl rounded-3xl p-2.5 border shadow-2xl" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
            <div className="relative rounded-2xl overflow-hidden aspect-[16/9] border" style={{ borderColor: "var(--border)" }}>
              <Image
                src="/images/atmosiq-hero.jpg"
                alt="AtmosIQ Global Atmospheric Weather Intelligence Radar Streamlines"
                fill
                priority
                className="object-cover"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-black/30 pointer-events-none" />

              {/* Floating Overlay Badge on Hero Image */}
              <div className="absolute bottom-6 left-6 right-6 p-4 sm:p-6 rounded-2xl border border-white/20 bg-slate-950/70 backdrop-blur-xl text-left flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
                    <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Live Synoptic Telemetry Stream</span>
                  </div>
                  <h3 className="text-lg sm:text-xl font-bold text-white mt-1">
                    Multi-Layer Radar & Atmospheric Isobars Active
                  </h3>
                  <p className="text-xs text-slate-300 mt-0.5">
                    32 Indian Stations · XGBoost, LightGBM & CatBoost Ensembles · Continuous Drift Monitoring
                  </p>
                </div>
                <Link href="/weather/map">
                  <Button size="sm" className="bg-sky-500 hover:bg-sky-400 text-slate-950 font-extrabold text-xs px-4 rounded-xl self-start sm:self-auto">
                    Open Radar Map <ArrowUpRight size={14} className="ml-1" />
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Enterprise Platform Stats Counter */}
      <section className="py-12 border-b" style={{ borderColor: "var(--border)", background: "var(--card)" }}>
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
          <div className="space-y-1">
            <p className="text-3xl sm:text-4xl font-extrabold text-blue-500">32+</p>
            <span className="text-xs font-bold uppercase tracking-wider block" style={{ color: "var(--foreground)" }}>Monitored Stations</span>
            <span className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>Synchronized across India</span>
          </div>

          <div className="space-y-1">
            <p className="text-3xl sm:text-4xl font-extrabold text-emerald-500">124</p>
            <span className="text-xs font-bold uppercase tracking-wider block" style={{ color: "var(--foreground)" }}>Trained ML Champions</span>
            <span className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>Multi-horizon ensembles</span>
          </div>

          <div className="space-y-1">
            <p className="text-3xl sm:text-4xl font-extrabold text-sky-400">0.69°C</p>
            <span className="text-xs font-bold uppercase tracking-wider block" style={{ color: "var(--foreground)" }}>Temperature MAE</span>
            <span className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>+37.3% vs Persistence</span>
          </div>

          <div className="space-y-1">
            <p className="text-3xl sm:text-4xl font-extrabold text-purple-500">99.8%</p>
            <span className="text-xs font-bold uppercase tracking-wider block" style={{ color: "var(--foreground)" }}>Data Quality Score</span>
            <span className="text-[11px]" style={{ color: "var(--muted-foreground)" }}>Zero feature leakage</span>
          </div>
        </div>
      </section>

      {/* 5. Core Platform Features Grid */}
      <section id="features" className="py-20 border-b" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 space-y-12">
          <div className="text-center max-w-3xl mx-auto space-y-3">
            <span className="text-xs font-extrabold uppercase tracking-wider text-blue-500">Platform Capabilities</span>
            <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight" style={{ color: "var(--foreground)" }}>
              Engineered for Precision Meteorology & MLOps
            </h2>
            <p className="text-sm leading-relaxed" style={{ color: "var(--muted-foreground)" }}>
              A full-stack machine learning weather ecosystem built from the ground up to solve forecasting uncertainty, data leakage, and drift.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Feature Card 1 */}
            <div className="p-6 rounded-2xl border transition-all hover:border-blue-500 shadow-xl space-y-3" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
              <div className="h-12 w-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-500">
                <Layers size={24} />
              </div>
              <h3 className="text-base font-extrabold" style={{ color: "var(--foreground)" }}>Multi-Horizon Forecasting</h3>
              <p className="text-xs leading-relaxed" style={{ color: "var(--muted-foreground)" }}>
                Dedicated specialized models trained independently for 1h, 3h, 6h, 12h, 24h, 48h, and 72h horizons with calibrated quantile intervals.
              </p>
            </div>

            {/* Feature Card 2 */}
            <div className="p-6 rounded-2xl border transition-all hover:border-cyan-500 shadow-xl space-y-3" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
              <div className="h-12 w-12 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-500">
                <Droplets size={24} />
              </div>
              <h3 className="text-base font-extrabold" style={{ color: "var(--foreground)" }}>Two-Stage Rain Hurdle</h3>
              <p className="text-xs leading-relaxed" style={{ color: "var(--muted-foreground)" }}>
                Dual-phase architecture: Stage 1 calculates calibrated rain occurrence probability, Stage 2 predicts exact precipitation millimeters.
              </p>
            </div>

            {/* Feature Card 3 */}
            <div className="p-6 rounded-2xl border transition-all hover:border-emerald-500 shadow-xl space-y-3" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
              <div className="h-12 w-12 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-500">
                <ShieldCheck size={24} />
              </div>
              <h3 className="text-base font-extrabold" style={{ color: "var(--foreground)" }}>Automated Quality Gates</h3>
              <p className="text-xs leading-relaxed" style={{ color: "var(--muted-foreground)" }}>
                Challenger models compete against Persistence & Climatology. Only candidate models beating MASE and skill thresholds are promoted to Champion.
              </p>
            </div>

            {/* Feature Card 4 */}
            <div className="p-6 rounded-2xl border transition-all hover:border-purple-500 shadow-xl space-y-3" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
              <div className="h-12 w-12 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center text-purple-500">
                <Activity size={24} />
              </div>
              <h3 className="text-base font-extrabold" style={{ color: "var(--foreground)" }}>Drift & Anomaly Sentinel</h3>
              <p className="text-xs leading-relaxed" style={{ color: "var(--muted-foreground)" }}>
                Population Stability Index (PSI) and Kolmogorov-Smirnov statistical tests continuously monitor feature distributions and trigger automated retraining.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 6. Interactive MLOps Dashboard Preview Section */}
      <section id="architecture" className="py-20 border-b" style={{ borderColor: "var(--border)", background: "var(--muted)" }}>
        <div className="max-w-7xl mx-auto px-6 space-y-12">
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
            <div>
              <span className="text-xs font-extrabold uppercase tracking-wider text-blue-500">Production Infrastructure</span>
              <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight mt-2" style={{ color: "var(--foreground)" }}>
                Full-Lifecycle MLOps Pipeline
              </h2>
              <p className="text-sm max-w-2xl mt-2" style={{ color: "var(--muted-foreground)" }}>
                From raw Open-Meteo & ERA5 ingestion to causal feature engineering, MLflow experiment tracking, and PostgreSQL prediction history.
              </p>
            </div>

            <Link href="/ml/models">
              <Button className="bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs rounded-xl shadow">
                Explore ML Models Registry <ArrowRight size={14} className="ml-1" />
              </Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
            {/* Left Preview Image */}
            <div className="lg:col-span-7 rounded-2xl overflow-hidden border shadow-2xl" style={{ borderColor: "var(--card-border)" }}>
              <div className="relative aspect-[16/9] w-full">
                <Image
                  src="/images/atmosiq-dashboard-preview.jpg"
                  alt="AtmosIQ MLOps Hub with 3D Radar, Neural Networks, Decision Trees, and Drift Monitoring"
                  fill
                  className="object-cover"
                />
              </div>
            </div>

            {/* Right Pipeline Steps */}
            <div className="lg:col-span-5 space-y-4">
              <div className="p-4 rounded-2xl border space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
                <div className="flex items-center gap-2">
                  <span className="h-6 w-6 rounded-lg bg-blue-500 text-white font-mono text-xs font-bold flex items-center justify-center">1</span>
                  <h4 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>Bronze/Silver Ingestion & LeakageGuard</h4>
                </div>
                <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
                  Hourly ingestion with strict causal time assertions. Lags strictly use shift(k &gt;= 1) to eliminate temporal lookahead leakage.
                </p>
              </div>

              <div className="p-4 rounded-2xl border space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
                <div className="flex items-center gap-2">
                  <span className="h-6 w-6 rounded-lg bg-emerald-500 text-white font-mono text-xs font-bold flex items-center justify-center">2</span>
                  <h4 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>Competitive ML Tournament</h4>
                </div>
                <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
                  XGBoost, LightGBM, CatBoost, and HistGradientBoosting compete across tasks (temperature, rain, wind, humidity) under walk-forward CV.
                </p>
              </div>

              <div className="p-4 rounded-2xl border space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
                <div className="flex items-center gap-2">
                  <span className="h-6 w-6 rounded-lg bg-purple-500 text-white font-mono text-xs font-bold flex items-center justify-center">3</span>
                  <h4 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>Automated Promotion & Deployment</h4>
                </div>
                <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
                  Winners are promoted to Champion stage in MLflow registry and hot-swapped for zero-downtime inference with single-digit millisecond latency.
                </p>
              </div>

              <div className="p-4 rounded-2xl border space-y-1" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
                <div className="flex items-center gap-2">
                  <span className="h-6 w-6 rounded-lg bg-cyan-500 text-white font-mono text-xs font-bold flex items-center justify-center">4</span>
                  <h4 className="text-sm font-bold" style={{ color: "var(--foreground)" }}>Continuous Verification & Feedback</h4>
                </div>
                <p className="text-xs" style={{ color: "var(--muted-foreground)" }}>
                  As observations materialize, forecasts are paired in real time to calculate verified ground-truth MAE, RMSE, and Brier scores.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 7. Benchmarks & Model Arena Comparison Table */}
      <section id="benchmarks" className="py-20 border-b" style={{ borderColor: "var(--border)" }}>
        <div className="max-w-7xl mx-auto px-6 space-y-8">
          <div className="text-center max-w-2xl mx-auto space-y-2">
            <span className="text-xs font-extrabold uppercase tracking-wider text-blue-500">Empirical Performance</span>
            <h2 className="text-3xl sm:text-4xl font-extrabold tracking-tight" style={{ color: "var(--foreground)" }}>
              AtmosIQ vs Traditional Baselines
            </h2>
            <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>
              Validation scores evaluated across multi-station Indian meteorological test splits.
            </p>
          </div>

          <div className="rounded-2xl border overflow-hidden shadow-xl" style={{ background: "var(--card)", borderColor: "var(--card-border)" }}>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b text-left font-bold" style={{ borderColor: "var(--border)", color: "var(--muted-foreground)", background: "var(--muted)" }}>
                    <th className="py-3.5 px-4">Forecasting Model / System</th>
                    <th className="py-3.5 px-4">Architecture Type</th>
                    <th className="py-3.5 px-4 text-right">Temp MAE (°C)</th>
                    <th className="py-3.5 px-4 text-right">Rain Brier Score</th>
                    <th className="py-3.5 px-4 text-right">Wind MAE (km/h)</th>
                    <th className="py-3.5 px-4 text-right">Skill vs Persistence</th>
                    <th className="py-3.5 px-4 text-right">Inference Latency</th>
                  </tr>
                </thead>
                <tbody className="divide-y font-medium" style={{ borderColor: "var(--border)" }}>
                  <tr className="bg-blue-500/10 font-bold">
                    <td className="py-3.5 px-4 flex items-center gap-2 text-blue-500">
                      <Award size={16} /> AtmosIQ Champion Ensemble
                    </td>
                    <td className="py-3.5 px-4 text-blue-600 dark:text-blue-300">LightGBM + XGBoost Quantile</td>
                    <td className="py-3.5 px-4 text-right text-emerald-500 font-extrabold">0.69°C</td>
                    <td className="py-3.5 px-4 text-right text-emerald-500 font-extrabold">0.124</td>
                    <td className="py-3.5 px-4 text-right text-emerald-500 font-extrabold">1.45 km/h</td>
                    <td className="py-3.5 px-4 text-right text-emerald-500 font-extrabold">+37.3%</td>
                    <td className="py-3.5 px-4 text-right font-mono text-cyan-500">12 ms</td>
                  </tr>
                  <tr>
                    <td className="py-3.5 px-4 font-semibold" style={{ color: "var(--foreground)" }}>CatBoost Candidate</td>
                    <td className="py-3.5 px-4" style={{ color: "var(--muted-foreground)" }}>Oblivious Decision Trees</td>
                    <td className="py-3.5 px-4 text-right font-bold" style={{ color: "var(--foreground)" }}>0.72°C</td>
                    <td className="py-3.5 px-4 text-right" style={{ color: "var(--muted-foreground)" }}>0.131</td>
                    <td className="py-3.5 px-4 text-right" style={{ color: "var(--muted-foreground)" }}>1.90 km/h</td>
                    <td className="py-3.5 px-4 text-right text-emerald-500">+31.2%</td>
                    <td className="py-3.5 px-4 text-right font-mono" style={{ color: "var(--muted-foreground)" }}>18 ms</td>
                  </tr>
                  <tr>
                    <td className="py-3.5 px-4 font-semibold" style={{ color: "var(--foreground)" }}>Global NWP Provider (ECMWF/GFS)</td>
                    <td className="py-3.5 px-4" style={{ color: "var(--muted-foreground)" }}>Numerical Weather Prediction</td>
                    <td className="py-3.5 px-4 text-right font-bold" style={{ color: "var(--foreground)" }}>1.05°C</td>
                    <td className="py-3.5 px-4 text-right" style={{ color: "var(--muted-foreground)" }}>0.165</td>
                    <td className="py-3.5 px-4 text-right" style={{ color: "var(--muted-foreground)" }}>2.80 km/h</td>
                    <td className="py-3.5 px-4 text-right text-cyan-500">+18.0%</td>
                    <td className="py-3.5 px-4 text-right font-mono" style={{ color: "var(--muted-foreground)" }}>3500 ms</td>
                  </tr>
                  <tr>
                    <td className="py-3.5 px-4 font-semibold" style={{ color: "var(--foreground)" }}>Persistence Baseline</td>
                    <td className="py-3.5 px-4" style={{ color: "var(--muted-foreground)" }}>Lag-1 Naive Persistence</td>
                    <td className="py-3.5 px-4 text-right text-rose-500 font-bold">1.16°C</td>
                    <td className="py-3.5 px-4 text-right text-rose-500">0.240</td>
                    <td className="py-3.5 px-4 text-right text-rose-500">3.70 km/h</td>
                    <td className="py-3.5 px-4 text-right text-rose-500">0.0% (Base)</td>
                    <td className="py-3.5 px-4 text-right font-mono" style={{ color: "var(--muted-foreground)" }}>&lt;1 ms</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </section>

      {/* 8. High-Conversion CTA Banner */}
      <section className="py-20 border-b relative overflow-hidden" style={{ borderColor: "var(--border)", background: "var(--card)" }}>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-blue-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="max-w-4xl mx-auto px-6 text-center space-y-6 relative z-10">
          <h2 className="text-3xl sm:text-5xl font-extrabold tracking-tight" style={{ color: "var(--foreground)" }}>
            Turn Atmospheric Chaos Into Deterministic Forecasts
          </h2>
          <p className="text-sm sm:text-base max-w-2xl mx-auto" style={{ color: "var(--muted-foreground)" }}>
            Deploy production weather ML pipelines with calibrated confidence bounds, automated retraining, and RESTful telemetry APIs.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4 pt-2">
            <Link href="/dashboard">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm px-8 rounded-xl shadow-xl shadow-blue-500/25">
                Launch AtmosIQ Dashboard <ArrowRight size={16} className="ml-1.5" />
              </Button>
            </Link>
            <Link href="/weather/map">
              <Button variant="secondary" size="lg" className="border text-sm font-bold px-8 rounded-xl" style={{ background: "var(--muted)", borderColor: "var(--border)", color: "var(--foreground)" }}>
                View Synoptic Radar
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* 9. Enterprise Footer */}
      <footer className="py-12 text-xs" style={{ background: "var(--background)", color: "var(--muted-foreground)" }}>
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2.5">
            <div className="h-7 w-7 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold">
              <CloudSun size={16} />
            </div>
            <span className="font-extrabold text-sm" style={{ color: "var(--foreground)" }}>AtmosIQ</span>
            <span>— Autonomous Weather Intelligence & MLOps Suite</span>
          </div>

          <div className="flex flex-wrap items-center gap-6 font-semibold">
            <Link href="/dashboard" className="hover:text-blue-500 transition-colors">Overview</Link>
            <Link href="/weather/hourly" className="hover:text-blue-500 transition-colors">Hourly Forecast</Link>
            <Link href="/weather/daily" className="hover:text-blue-500 transition-colors">Daily Forecast</Link>
            <Link href="/weather/map" className="hover:text-blue-500 transition-colors">Radar Map</Link>
            <Link href="/forecast/comparison" className="hover:text-blue-500 transition-colors">Forecast Comparison</Link>
            <Link href="/ml/models" className="hover:text-blue-500 transition-colors">ML Registry</Link>
            <a href="http://127.0.0.1:8001/docs" target="_blank" className="hover:text-blue-500 transition-colors">API Docs</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
