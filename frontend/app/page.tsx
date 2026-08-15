"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  CloudSun,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Zap,
  Activity,
  Layers,
  BarChart3,
  Cpu,
  Droplets,
  Wind,
  Search,
  CheckCircle2,
  Gauge,
  Lock,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { WeatherIcon } from "@/components/ui/weather-icon";

export default function LandingPage() {
  const [searchLocation, setSearchLocation] = useState("Kavali, Andhra Pradesh");

  return (
    <div className="min-h-screen bg-[#070D1E] text-slate-100 selection:bg-sky-500 selection:text-white font-sans">
      {/* 1. Sticky Glass Header */}
      <header className="sticky top-0 z-50 w-full bg-[#070D1E]/80 backdrop-blur-lg border-b border-slate-800/80 transition-all">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-lg bg-gradient-to-br from-sky-400 via-blue-600 to-indigo-700 flex items-center justify-center text-white shadow-md shadow-sky-500/20">
              <CloudSun size={20} className="text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white font-sans">
              Atmos<span className="text-sky-400">IQ</span>
            </span>
          </Link>

          <nav className="hidden md:flex items-center gap-8 text-xs font-medium text-slate-300">
            <a href="#capabilities" className="hover:text-sky-400 transition-colors">Product</a>
            <Link href="/dashboard" className="hover:text-sky-400 transition-colors">Forecast</Link>
            <Link href="/dashboard" className="hover:text-sky-400 transition-colors">Intelligence</Link>
            <a href="#models" className="hover:text-sky-400 transition-colors">Models</a>
            <a href="#monitoring" className="hover:text-sky-400 transition-colors">Monitoring</a>
            <a href="http://127.0.0.1:8000/docs" target="_blank" className="hover:text-sky-400 transition-colors">Docs</a>
          </nav>

          <div className="flex items-center gap-3">
            <Link href="/dashboard">
              <Button variant="ghost" size="sm" className="hidden sm:inline-flex text-xs font-semibold">
                Sign In
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="primary" size="sm" className="text-xs font-semibold px-4">
                Explore Platform <ArrowRight size={14} />
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* 2. Hero Section */}
      <section className="relative pt-16 pb-24 overflow-hidden">
        {/* Background Atmospheric Glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[400px] bg-gradient-to-tr from-sky-600/15 via-blue-500/20 to-indigo-600/10 rounded-full blur-3xl pointer-events-none -z-10" />

        <div className="max-w-7xl mx-auto px-6 flex flex-col items-center text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-500/10 border border-sky-500/20 text-sky-400 text-xs font-semibold mb-6 animate-fade-in">
            <Sparkles size={14} className="text-sky-400" />
            <span>Next-Gen Enterprise Weather Intelligence Platform</span>
          </div>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-white max-w-4xl leading-[1.1] font-sans">
            AI-Powered <br className="hidden sm:block" />
            <span className="bg-gradient-to-r from-sky-400 via-blue-300 to-indigo-200 bg-clip-text text-transparent">
              Weather Intelligence
            </span>
          </h1>

          <p className="mt-6 text-base sm:text-lg text-slate-300 max-w-2xl leading-relaxed">
            Forecast temperature, rainfall, wind, and severe weather risk with production-grade machine learning.
            Multi-horizon quantile ensembles with automated continuous MLOps monitoring.
          </p>

          {/* Search Bar / Location Input */}
          <div className="mt-8 w-full max-w-lg bg-slate-900/90 border border-slate-700/80 rounded-2xl p-2 flex items-center gap-2 shadow-2xl shadow-black/50 backdrop-blur-md">
            <div className="p-2.5 text-sky-400">
              <Search size={18} />
            </div>
            <input
              type="text"
              value={searchLocation}
              onChange={(e) => setSearchLocation(e.target.value)}
              placeholder="Search station or city (e.g. Kavali, Hyderabad)..."
              className="bg-transparent flex-1 text-sm text-slate-100 placeholder-slate-400 focus:outline-none"
            />
            <Link href="/dashboard">
              <Button size="sm" className="rounded-xl text-xs font-semibold px-4">
                Get Forecast
              </Button>
            </Link>
          </div>

          {/* Hero Buttons */}
          <div className="mt-6 flex flex-wrap items-center justify-center gap-4">
            <Link href="/dashboard">
              <Button size="lg" className="text-sm font-semibold shadow-lg shadow-sky-500/25">
                Explore Forecast <ArrowRight size={16} />
              </Button>
            </Link>
            <Link href="/dashboard">
              <Button variant="secondary" size="lg" className="text-sm font-semibold">
                View Intelligence Suite
              </Button>
            </Link>
          </div>

          {/* 3. Interactive Hero Preview Card */}
          <div className="mt-14 w-full max-w-5xl rounded-2xl p-2 bg-gradient-to-b from-slate-700/40 via-slate-800/20 to-transparent border border-slate-800 shadow-2xl shadow-black/80">
            <Card className="p-6 bg-[#0B132B] border-slate-800/90 rounded-xl text-left">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-slate-800 border border-slate-700">
                    <WeatherIcon code={2} size={32} />
                  </div>
                  <div>
                    <span className="text-xs text-slate-400 font-semibold uppercase tracking-wider">Live AI Forecast</span>
                    <h3 className="text-base font-bold text-white font-sans">Kavali, Andhra Pradesh · Station 43245</h3>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="success">124 Models Champion</Badge>
                  <Badge variant="info">LightGBM Quantile (p10 / p50 / p90)</Badge>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-5">
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                  <span className="text-xs text-slate-400">24h Predicted Temp</span>
                  <p className="text-2xl font-bold text-white mt-1">29.1°C</p>
                  <span className="text-[11px] text-slate-400">Interval [28.1°C – 29.8°C]</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                  <span className="text-xs text-slate-400">Rain Probability</span>
                  <p className="text-2xl font-bold text-sky-400 mt-1">62%</p>
                  <span className="text-[11px] text-slate-400">Expected: 0.32 mm (Light)</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                  <span className="text-xs text-slate-400">Surface Wind</span>
                  <p className="text-2xl font-bold text-teal-400 mt-1">12.6 km/h</p>
                  <span className="text-[11px] text-slate-400">Gusts up to 21.9 km/h (NW)</span>
                </div>
                <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
                  <span className="text-xs text-slate-400">Model Skill vs Baseline</span>
                  <p className="text-2xl font-bold text-emerald-400 mt-1">0.82</p>
                  <span className="text-[11px] text-emerald-400">+18% vs Persistence</span>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* 4. Trust & Capability Grid */}
      <section id="capabilities" className="py-20 border-t border-slate-800/80 bg-slate-950/40">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-2xl mx-auto">
            <span className="text-xs font-semibold uppercase tracking-wider text-sky-400">Core Capabilities</span>
            <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight mt-2 font-sans">
              Engineered for Mission-Critical Accuracy
            </h2>
            <p className="text-sm text-slate-400 mt-3">
              Combining physical ERA5 atmospheric telemetry with gradient boosting and deep learning time series architectures.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-14">
            <Card className="p-6 bg-slate-900 border-slate-800/90 hover:border-sky-500/40 transition-all">
              <div className="p-3 rounded-xl bg-sky-500/10 text-sky-400 w-fit">
                <Layers size={22} />
              </div>
              <h3 className="text-base font-bold text-white mt-4 font-sans">Multi-Horizon Forecasting</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Independent probabilistic models for 1h, 3h, 6h, 12h, 24h, 48h, and 72h lead times with calibrated uncertainty intervals.
              </p>
            </Card>

            <Card className="p-6 bg-slate-900 border-slate-800/90 hover:border-sky-500/40 transition-all">
              <div className="p-3 rounded-xl bg-blue-500/10 text-blue-400 w-fit">
                <Droplets size={22} />
              </div>
              <h3 className="text-base font-bold text-white mt-4 font-sans">Rain Intelligence</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Precision rain occurrence classification and quantitative precipitation estimation with multi-level intensity thresholds.
              </p>
            </Card>

            <Card className="p-6 bg-slate-900 border-slate-800/90 hover:border-sky-500/40 transition-all">
              <div className="p-3 rounded-xl bg-indigo-500/10 text-indigo-400 w-fit">
                <Cpu size={22} />
              </div>
              <h3 className="text-base font-bold text-white mt-4 font-sans">Automated Quality Gates</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Challenger models compete against persistence baselines. Only models surpassing strict MASE & skill thresholds become Champions.
              </p>
            </Card>

            <Card className="p-6 bg-slate-900 border-slate-800/90 hover:border-sky-500/40 transition-all">
              <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 w-fit">
                <Activity size={22} />
              </div>
              <h3 className="text-base font-bold text-white mt-4 font-sans">Continuous Drift Monitoring</h3>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Real-time Kolmogorov-Smirnov and Population Stability Index (PSI) tracking to detect feature distribution shifts and trigger retraining.
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* 5. AI Models in Competition */}
      <section id="models" className="py-20 border-t border-slate-800/80">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
            <div>
              <span className="text-xs font-semibold uppercase tracking-wider text-sky-400">Model Architecture</span>
              <h2 className="text-3xl sm:text-4xl font-bold text-white tracking-tight mt-2 font-sans">
                Competitive ML Arena
              </h2>
              <p className="text-sm text-slate-400 mt-2 max-w-xl">
                Every forecast horizon hosts competing algorithms. The platform continuously evaluates validation metrics to promote the winning Champion.
              </p>
            </div>
            <Link href="/dashboard">
              <Button variant="outline" size="sm">
                View Full Leaderboard <ArrowRight size={14} />
              </Button>
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
            <Card className="p-6 bg-slate-900 border-slate-800">
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-white font-sans">LightGBM & XGBoost</span>
                <Badge variant="success">Champion</Badge>
              </div>
              <p className="text-xs text-slate-400 mt-2">
                Ultra-fast gradient boosting with custom quantile loss functions for asymmetric temperature and rainfall prediction.
              </p>
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-300 font-medium">
                <span>MAE: 1.42°C</span>
                <span className="text-emerald-400">Skill: 0.82</span>
              </div>
            </Card>

            <Card className="p-6 bg-slate-900 border-slate-800">
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-white font-sans">Random Forest & Ridge</span>
                <Badge variant="info">Ensemble</Badge>
              </div>
              <p className="text-xs text-slate-400 mt-2">
                Robust bagging and regularized linear baselines ensuring stability across volatile microclimate transitions.
              </p>
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-300 font-medium">
                <span>MAE: 1.85°C</span>
                <span className="text-sky-400">Skill: 0.65</span>
              </div>
            </Card>

            <Card className="p-6 bg-slate-900 border-slate-800">
              <div className="flex items-center justify-between">
                <span className="text-sm font-bold text-white font-sans">Deep LSTM & TCN</span>
                <Badge variant="purple">Sequential</Badge>
              </div>
              <p className="text-xs text-slate-400 mt-2">
                Recurrent neural networks and temporal convolutional architectures capturing multi-day synoptic weather momentum.
              </p>
              <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-300 font-medium">
                <span>MAE: 1.66°C</span>
                <span className="text-indigo-400">Skill: 0.74</span>
              </div>
            </Card>
          </div>
        </div>
      </section>

      {/* 6. Final Call to Action */}
      <section className="py-20 border-t border-slate-800/80 bg-gradient-to-b from-[#070D1E] to-[#0B132B]">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight font-sans">
            Turn Weather Data Into Intelligent Decisions
          </h2>
          <p className="text-slate-300 mt-4 text-sm sm:text-base max-w-xl mx-auto">
            Ready to integrate production-grade weather predictions and automated model monitoring into your workflow?
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
            <Link href="/dashboard">
              <Button size="lg" className="font-semibold text-sm px-6">
                Explore AtmosIQ Dashboard <ArrowRight size={16} />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* 7. Enterprise Footer */}
      <footer className="py-12 border-t border-slate-800 bg-[#070D1E] text-xs text-slate-400">
        <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-2">
            <CloudSun size={18} className="text-sky-400" />
            <span className="text-slate-200 font-bold">AtmosIQ</span>
            <span>— AI-Powered Weather Intelligence & MLOps Platform</span>
          </div>
          <div className="flex items-center gap-6">
            <Link href="/dashboard" className="hover:text-white transition-colors">Overview</Link>
            <Link href="/dashboard" className="hover:text-white transition-colors">Models</Link>
            <Link href="/dashboard" className="hover:text-white transition-colors">Monitoring</Link>
            <a href="http://127.0.0.1:8000/docs" target="_blank" className="hover:text-white transition-colors">API Docs</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
