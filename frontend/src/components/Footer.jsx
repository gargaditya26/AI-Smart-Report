const Footer = () => {
  return (
    <footer className="bg-slate-950 border-t border-slate-800 mt-16 text-slate-300">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid md:grid-cols-3 gap-8">
          <div>
            <h3 className="font-semibold text-white mb-3">Privacy & Security</h3>
            <ul className="space-y-2 text-sm text-slate-400">
              <li>✓ No permanent storage of your reports</li>
              <li>✓ All data auto-deleted after 1 hour</li>
              <li>✓ Privacy-focused processing</li>
              <li>✓ Temporary session data</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-white mb-3">How It Works</h3>
            <ul className="space-y-2 text-sm text-slate-400">
              <li>1. Upload your pathology report</li>
              <li>2. AI extracts lab test results</li>
              <li>3. Review and edit results</li>
              <li>4. Get organ health analysis</li>
              <li>5. Download PDF report</li>
            </ul>
          </div>
          <div>
            <h3 className="font-semibold text-white mb-3">Disclaimer</h3>
            <p className="text-sm text-slate-400">
              This tool is for informational purposes only and is not a substitute
              for professional medical advice, diagnosis, or treatment. Always
              consult your physician for health concerns.
            </p>
          </div>
        </div>
        <div className="mt-8 pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3 text-sm text-slate-500">
          <p>© 2026 SmartReports. All rights reserved.</p>
          <div className="flex items-center gap-2">
            <span>Product by</span>
            <span className="text-blue-400 font-semibold">OPSNORA</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
