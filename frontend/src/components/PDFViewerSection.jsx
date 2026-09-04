import { Download, Trash2, RotateCcw } from 'lucide-react';
import { getPDFUrl } from '../services/api';

const PDFViewerSection = ({ pdfData, onStartOver }) => {
  const pdfUrl = getPDFUrl(pdfData.pdf_id);

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = `${pdfUrl}/download`;
    link.download = `smartreports_health_analysis_${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="max-w-5xl mx-auto">
      <div className="card">
        <div className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Your Health Report is Ready!</h2>
          <p className="text-gray-600">
            Generated on {new Date(pdfData.generation_date).toLocaleString()}
          </p>
        </div>

        {/* Privacy Notice */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
          <p className="text-sm text-green-800">
            ✓ Your uploaded report and extracted data have been permanently deleted.
            Only this generated PDF is stored temporarily.
          </p>
        </div>

        {/* PDF Viewer */}
        <div className="bg-gray-100 rounded-lg p-4 mb-6">
          <iframe
            src={pdfUrl}
            className="w-full h-[600px] rounded border border-gray-300"
            title="Health Report PDF"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap gap-4 justify-center">
          <button
            onClick={handleDownload}
            className="btn-primary text-lg px-8 py-4 flex items-center gap-2"
          >
            <Download className="w-5 h-5" />
            Download PDF
          </button>

          <button
            onClick={onStartOver}
            className="btn-secondary flex items-center gap-2"
          >
            <RotateCcw className="w-5 h-5" />
            Analyze Another Report
          </button>
        </div>

        {/* Info */}
        <div className="mt-6 text-center text-sm text-gray-600">
          <p>This PDF will be available for 24 hours.</p>
          <p className="mt-1">You can delete it immediately if you prefer.</p>
        </div>
      </div>
    </div>
  );
};

export default PDFViewerSection;
