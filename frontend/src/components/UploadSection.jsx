import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, Shield, Info } from 'lucide-react';

const UploadSection = ({ onFileUpload, isVisible, isLoading }) => {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onFileUpload(acceptedFiles[0]);
    }
  }, [onFileUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxSize: 10485760, // 10MB
    multiple: false,
    disabled: isLoading
  });

  if (!isVisible) return null;

  return (
    <div className="max-w-4xl mx-auto">
      {/* Privacy Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-8">
        <div className="flex items-start gap-3">
          <Shield className="w-6 h-6 text-primary flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-gray-900 mb-2">Your Privacy is Our Priority</h3>
            <ul className="text-sm text-gray-700 space-y-1">
              <li>✓ We do not permanently store your uploaded report</li>
              <li>✓ All data is automatically deleted after 1 hour</li>
              <li>✓ Only the generated PDF is saved temporarily (you can delete it anytime)</li>
              <li>✓ No personal health information is retained</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Upload Area */}
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Upload Your Pathology Report</h2>

        <div
          {...getRootProps()}
          className={`
            border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
            transition-all duration-200
            ${isDragActive
              ? 'border-primary bg-blue-50 scale-105'
              : 'border-gray-300 hover:border-primary hover:bg-gray-50'
            }
            ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}
          `}
        >
          <input {...getInputProps()} />

          <div className="flex flex-col items-center gap-4">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
              <Upload className="w-8 h-8 text-primary" />
            </div>

            {isDragActive ? (
              <p className="text-lg font-medium text-primary">Drop your file here</p>
            ) : (
              <>
                <div>
                  <p className="text-lg font-medium text-gray-900 mb-2">
                    Drag and drop your report here, or click to browse
                  </p>
                  <p className="text-sm text-gray-600">
                    Supported formats: PDF, TXT, JPG, PNG, DOCX
                  </p>
                </div>
              </>
            )}

            <div className="flex items-center gap-2 text-sm text-gray-500">
              <FileText className="w-4 h-4" />
              <span>Maximum file size: 10MB</span>
            </div>
          </div>
        </div>

        {/* Info Box */}
        <div className="mt-6 bg-gray-50 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <Info className="w-5 h-5 text-gray-600 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-gray-700">
              <p className="font-medium mb-1">What happens next?</p>
              <ol className="list-decimal list-inside space-y-1 ml-2">
                <li>Your file will be scanned for viruses</li>
                <li>Text will be extracted using AI/OCR</li>
                <li>Lab test results will be automatically identified</li>
                <li>You can review and edit the results</li>
                <li>Organ health analysis will be generated</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadSection;
