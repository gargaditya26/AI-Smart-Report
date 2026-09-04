import { Shield, Sparkles } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-slate-950 border-b border-slate-800 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-11 h-11 rounded-xl bg-white/10 border border-white/10 flex items-center justify-center shrink-0">
              <Sparkles className="w-6 h-6 text-blue-400" />
            </div>
            <div className="min-w-0">
              <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">SmartReports</h1>
              <p className="text-xs sm:text-sm text-slate-400 truncate">AI-Powered Health Report Analyzer</p>
            </div>
          </div>

          <div className="flex items-center gap-3 shrink-0">
            <div className="hidden sm:flex items-center gap-2 bg-emerald-400/10 border border-emerald-400/20 px-3 py-2 rounded-lg">
              <Shield className="w-4 h-4 text-emerald-400" />
              <span className="text-xs font-medium text-slate-300">Privacy First</span>
            </div>
            <div className="hidden xs:block h-8 w-px bg-slate-700" />
            <div className="flex items-center rounded-lg bg-white px-2.5 py-1.5 shadow-sm">
              <img
                src="/opsnora-logo.png"
                alt="OPSNORA"
                className="h-8 w-auto max-w-[150px] object-contain"
              />
            </div>
          </div>
        </div>

        <div className="mt-3 flex items-center justify-center sm:justify-end">
          <span className="text-[11px] tracking-wide text-slate-500">
            A product by <span className="text-blue-400 font-semibold">OPSNORA</span> · Automate. Innovate. Elevate.
          </span>
        </div>
      </div>
    </header>
  );
};

export default Header;
