import React, { useState, useEffect } from "react";
import { Send, Search, LayoutDashboard, BarChart3, Landmark, Cpu, ShieldCheck } from "lucide-react";
import SubmitComplaint from "./pages/SubmitComplaint";
import TrackComplaint from "./pages/TrackComplaint";
import AdminDashboard from "./pages/AdminDashboard";
import ComplaintDetails from "./pages/ComplaintDetails";
import Analytics from "./pages/Analytics";

export default function App() {
  const [tab, setTab] = useState("submit");
  const [selectedComplaintId, setSelectedComplaintId] = useState(null);

  // Synchronize state with hash routing if user clicks quick navigation links
  useEffect(() => {
    const handleHashRoute = () => {
      const hash = window.location.hash;
      if (hash.startsWith("#track")) {
        setTab("track");
      }
    };
    handleHashRoute();
    window.addEventListener("hashchange", handleHashRoute);
    return () => window.removeEventListener("hashchange", handleHashRoute);
  }, []);

  const renderContent = () => {
    switch (tab) {
      case "submit":
        return <SubmitComplaint />;
      case "track":
        return <TrackComplaint />;
      case "admin":
        if (selectedComplaintId) {
          return (
            <ComplaintDetails 
              complaintId={selectedComplaintId} 
              onBack={() => setSelectedComplaintId(null)} 
            />
          );
        }
        return <AdminDashboard onSelectComplaint={(id) => setSelectedComplaintId(id)} />;
      case "analytics":
        return <Analytics />;
      default:
        return <SubmitComplaint />;
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F8FA]">
      
      {/* Top Header */}
      <header className="bg-white border-b border-slate-100 shadow-sm sticky top-0 z-40">
        {/* Tricolor Header line */}
        <div className="h-1 w-full bg-gradient-to-r from-orange-500 via-white to-green-600" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex items-center justify-between">
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => { setTab("submit"); setSelectedComplaintId(null); }}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-gov-primary to-gov-secondary flex items-center justify-center text-white shadow-md shadow-gov-primary/10">
              <Landmark className="w-5.5 h-5.5 text-gov-gold" />
            </div>
            <div>
              <span className="text-base font-black tracking-tight text-gov-primary block flex items-center">
                Jansathi AI
                <span className="ml-1.5 px-2 py-0.5 bg-gov-secondary/15 rounded-full text-[9px] font-black text-gov-secondary flex items-center border border-gov-secondary/20">
                  <Cpu className="w-2.5 h-2.5 mr-0.5 animate-pulse" />
                  UP-GRID V2
                </span>
              </span>
              <span className="text-[10px] text-slate-400 font-semibold block uppercase tracking-widest mt-0.5">AI-Powered Grievance Portal</span>
            </div>
          </div>

          {/* Navigation tabs */}
          <nav className="flex space-x-1.5 bg-slate-100/80 p-1.5 rounded-xl border border-slate-200/50">
            <button
              onClick={() => { setTab("submit"); setSelectedComplaintId(null); }}
              className={`flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                tab === "submit" 
                  ? "bg-white text-gov-primary shadow-sm" 
                  : "text-slate-500 hover:text-slate-800 hover:bg-white/40"
              }`}
            >
              <Send className="w-4 h-4" />
              <span>File Grievance</span>
            </button>

            <button
              onClick={() => { setTab("track"); setSelectedComplaintId(null); }}
              className={`flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                tab === "track" 
                  ? "bg-white text-gov-primary shadow-sm" 
                  : "text-slate-500 hover:text-slate-800 hover:bg-white/40"
              }`}
            >
              <Search className="w-4 h-4" />
              <span>Track Ticket</span>
            </button>

            <button
              onClick={() => { setTab("admin"); setSelectedComplaintId(null); }}
              className={`flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                tab === "admin" 
                  ? "bg-white text-gov-primary shadow-sm" 
                  : "text-slate-500 hover:text-slate-800 hover:bg-white/40"
              }`}
            >
              <LayoutDashboard className="w-4 h-4" />
              <span>Admin Panel</span>
            </button>

            <button
              onClick={() => { setTab("analytics"); setSelectedComplaintId(null); }}
              className={`flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                tab === "analytics" 
                  ? "bg-white text-gov-primary shadow-sm" 
                  : "text-slate-500 hover:text-slate-800 hover:bg-white/40"
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Analytics</span>
            </button>
          </nav>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderContent()}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-100 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-2">
          <div className="flex items-center justify-center space-x-2 text-slate-400 text-xs font-semibold uppercase tracking-wider">
            <ShieldCheck className="w-4.5 h-4.5 text-gov-secondary" />
            <span>Government of Uttar Pradesh Grievance Ingestion Service</span>
          </div>
          <p className="text-[10px] text-slate-400 max-w-md mx-auto">
            Powered by Jansathi AI Agent network. Built for Smart Governance. Auto-escalation checks active.
          </p>
        </div>
      </footer>
    </div>
  );
}
