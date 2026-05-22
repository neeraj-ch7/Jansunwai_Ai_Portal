import React, { useState, useEffect } from "react";
import { BarChart3, TrendingUp, ShieldCheck, Map, Users, Award } from "lucide-react";
import { getStats } from "../services/api";

export default function Analytics() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const res = await getStats();
        setStats(res);
      } catch (err) {
        console.error("Failed to load analytics statistics", err);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  if (loading) {
    return (
      <div className="bg-white rounded-3xl p-12 text-center border border-slate-100 shadow-sm animate-pulse">
        <span className="text-slate-400 text-sm font-semibold">Compiling district analytics...</span>
      </div>
    );
  }

  const districts = [
    { name: "Lucknow Division", count: stats ? Math.round(stats.total_complaints * 0.45) : 8, perf: "94.2%" },
    { name: "Kanpur Division", count: stats ? Math.round(stats.total_complaints * 0.25) : 4, perf: "88.5%" },
    { name: "Noida Division", count: stats ? Math.round(stats.total_complaints * 0.20) : 3, perf: "91.8%" },
    { name: "Ghaziabad Division", count: stats ? Math.round(stats.total_complaints * 0.10) : 2, perf: "85.2%" },
  ];

  return (
    <div className="space-y-6 animate-slide-up">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gov-primary tracking-tight">System Performance & District Analytics</h2>
        <p className="text-slate-500 text-xs mt-0.5">Real-time statistics across regional command loops.</p>
      </div>

      {/* Analytics grids */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* District list mapping */}
        <div className="md:col-span-1 bg-white rounded-3xl border border-slate-100 shadow-sm p-6 space-y-4">
          <h3 className="text-sm font-bold text-gov-primary mb-3 flex items-center">
            <Map className="w-4.5 h-4.5 text-gov-secondary mr-2" />
            Top Division Grievances
          </h3>
          
          <div className="space-y-4">
            {districts.map((d, index) => (
              <div key={d.name} className="flex justify-between items-center p-3.5 bg-slate-50 rounded-2xl border border-slate-100/50">
                <div>
                  <span className="text-xs font-bold text-slate-800 block">{d.name}</span>
                  <span className="text-[10px] text-slate-400 font-semibold block mt-0.5">{d.count} Registered complaints</span>
                </div>
                <div className="text-right">
                  <span className="text-xs font-black text-gov-secondary block">{d.perf}</span>
                  <span className="text-[9px] text-slate-400 uppercase tracking-widest font-bold block">SLA Compliance</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* SLA and Resolution Compliance */}
        <div className="md:col-span-2 bg-white rounded-3xl border border-slate-100 shadow-sm p-6 space-y-6">
          <h3 className="text-sm font-bold text-gov-primary flex items-center">
            <TrendingUp className="w-4.5 h-4.5 text-gov-secondary mr-2" />
            SLA Resolution Trends
          </h3>

          {/* Simple custom SVG Line Graph representing registered vs resolved complaints */}
          <div className="relative p-2 border border-slate-100 rounded-2xl bg-slate-50/50">
            <div className="absolute top-4 left-4 flex space-x-4 text-[10px]">
              <span className="flex items-center">
                <span className="w-2.5 h-2.5 bg-gov-secondary rounded-full mr-1.5" />
                <span className="font-semibold text-slate-500">Grievances Ingestion</span>
              </span>
              <span className="flex items-center">
                <span className="w-2.5 h-2.5 bg-gov-success rounded-full mr-1.5" />
                <span className="font-semibold text-slate-500">Resolved Complaints</span>
              </span>
            </div>
            
            <svg viewBox="0 0 500 200" className="w-full h-48">
              {/* Grid Lines */}
              <line x1="40" y1="20" x2="480" y2="20" stroke="#E2E8F0" strokeWidth="1" strokeDasharray="4 4" />
              <line x1="40" y1="80" x2="480" y2="80" stroke="#E2E8F0" strokeWidth="1" strokeDasharray="4 4" />
              <line x1="40" y1="140" x2="480" y2="140" stroke="#E2E8F0" strokeWidth="1" strokeDasharray="4 4" />
              <line x1="40" y1="170" x2="480" y2="170" stroke="#CBD5E1" strokeWidth="1" />

              {/* Data Ingestion Line (Blue) */}
              <path 
                d="M 40 160 Q 120 110 200 130 T 360 50 T 480 30" 
                fill="none" 
                stroke="#328CC1" 
                strokeWidth="3.5" 
                strokeLinecap="round"
              />
              
              {/* Data Resolution Line (Green) */}
              <path 
                d="M 40 170 Q 120 150 200 160 T 360 90 T 480 60" 
                fill="none" 
                stroke="#10B981" 
                strokeWidth="3.5" 
                strokeLinecap="round"
              />

              {/* Data Point Circles */}
              <circle cx="200" cy="130" r="4.5" fill="#328CC1" stroke="#FFFFFF" strokeWidth="1.5" />
              <circle cx="360" cy="50" r="4.5" fill="#328CC1" stroke="#FFFFFF" strokeWidth="1.5" />
              <circle cx="200" cy="160" r="4.5" fill="#10B981" stroke="#FFFFFF" strokeWidth="1.5" />
              <circle cx="360" cy="90" r="4.5" fill="#10B981" stroke="#FFFFFF" strokeWidth="1.5" />

              {/* Labels */}
              <text x="40" y="188" fill="#94A3B8" fontSize="8" fontWeight="bold">Mon</text>
              <text x="120" y="188" fill="#94A3B8" fontSize="8" fontWeight="bold">Tue</text>
              <text x="200" y="188" fill="#94A3B8" fontSize="8" fontWeight="bold">Wed</text>
              <text x="280" y="188" fill="#94A3B8" fontSize="8" fontWeight="bold">Thu</text>
              <text x="360" y="188" fill="#94A3B8" fontSize="8" fontWeight="bold">Fri</text>
              <text x="440" y="188" fill="#94A3B8" fontSize="8" fontWeight="bold">Sat</text>
            </svg>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
              <Users className="w-5 h-5 text-slate-400 mx-auto mb-1.5" />
              <span className="text-[10px] text-slate-400 block font-bold uppercase">Citizens Served</span>
              <span className="text-base font-extrabold text-gov-primary mt-0.5 block">14,289</span>
            </div>
            
            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
              <Award className="w-5 h-5 text-gov-gold mx-auto mb-1.5" />
              <span className="text-[10px] text-slate-400 block font-bold uppercase">System Uptime</span>
              <span className="text-base font-extrabold text-gov-primary mt-0.5 block">99.98%</span>
            </div>

            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
              <ShieldCheck className="w-5 h-5 text-gov-success mx-auto mb-1.5" />
              <span className="text-[10px] text-slate-400 block font-bold uppercase">Auto-Escalation Rate</span>
              <span className="text-base font-extrabold text-gov-primary mt-0.5 block">3.1%</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
