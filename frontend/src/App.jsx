import { useState } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import Header from './components/Header';
import UploadSection from './components/UploadSection';
import ProcessingSection from './components/ProcessingSection';
import LabResultsSection from './components/LabResultsSection';
import OrganHealthSection from './components/OrganHealthSection';
import PDFViewerSection from './components/PDFViewerSection';
import Footer from './components/Footer';
import {
  uploadFile,
  extractLabTests,
  getLabResults,
  updateLabResults,
  addManualTest,
  deleteTest,
  calculateOrganScores,
  getOrganScores,
  generatePDF,
  deleteSession,
} from './services/api';

function App() {
  const [currentStage, setCurrentStage] = useState('upload'); // upload, processing, results, analysis, pdf
  const [sessionId, setSessionId] = useState(null);
  const [uploadedFile, setUploadedFile] = useState(null);
  const [processingStage, setProcessingStage] = useState('upload');
  const [labResults, setLabResults] = useState([]);
  const [organScores, setOrganScores] = useState(null);
  const [pdfData, setPdfData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileUpload = async (file) => {
    setIsLoading(true);
    setUploadedFile(file);
    setCurrentStage('processing');
    setProcessingStage('upload');

    try {
      // Upload file
      const uploadResponse = await uploadFile(file);
      setSessionId(uploadResponse.session_id);
      setProcessingStage('extraction');

      // Extract lab tests
      const extractResponse = await extractLabTests(uploadResponse.session_id);
      setLabResults(extractResponse.lab_results || []);
      setProcessingStage('completed');

      toast.success('File processed successfully!');
      setTimeout(() => {
        setCurrentStage('results');
      }, 1000);

    } catch (error) {
      console.error('Upload error:', error);
      toast.error(error.response?.data?.detail || 'Failed to process file');
      setCurrentStage('upload');
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateLabResults = async (updatedResults) => {
    try {
      await updateLabResults(sessionId, updatedResults);
      setLabResults(updatedResults);
      toast.success('Results updated successfully');
    } catch (error) {
      console.error('Update error:', error);
      toast.error('Failed to update results');
    }
  };

  const handleAddTest = async (testData) => {
    try {
      const response = await addManualTest(sessionId, testData);
      setLabResults([...labResults, response.test]);
      toast.success('Test added successfully');
    } catch (error) {
      console.error('Add test error:', error);
      toast.error('Failed to add test');
    }
  };

  const handleDeleteTest = async (testId) => {
    try {
      await deleteTest(sessionId, testId);
      setLabResults(labResults.filter(test => test.test_id !== testId));
      toast.success('Test deleted successfully');
    } catch (error) {
      console.error('Delete test error:', error);
      toast.error('Failed to delete test');
    }
  };

  const handleAnalyzeHealth = async () => {
    setIsLoading(true);

    try {
      await calculateOrganScores(sessionId);
      const scoresResponse = await getOrganScores(sessionId);
      setOrganScores(scoresResponse);
      setCurrentStage('analysis');
      toast.success('Health analysis completed!');
    } catch (error) {
      console.error('Analysis error:', error);
      toast.error('Failed to analyze health data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGeneratePDF = async () => {
    setIsLoading(true);

    try {
      const pdfResponse = await generatePDF(sessionId);
      setPdfData(pdfResponse);
      setCurrentStage('pdf');
      toast.success('PDF generated successfully!');
    } catch (error) {
      console.error('PDF generation error:', error);
      toast.error('Failed to generate PDF');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartOver = async () => {
    if (sessionId) {
      try {
        await deleteSession(sessionId);
      } catch (error) {
        console.error('Session delete error:', error);
      }
    }

    setSessionId(null);
    setUploadedFile(null);
    setLabResults([]);
    setOrganScores(null);
    setPdfData(null);
    setCurrentStage('upload');
    setProcessingStage('upload');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />
      <Header />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Upload Section */}
        <UploadSection
          onFileUpload={handleFileUpload}
          isVisible={currentStage === 'upload'}
          isLoading={isLoading}
        />

        {/* Processing Section */}
        {currentStage === 'processing' && (
          <ProcessingSection stage={processingStage} />
        )}

        {/* Lab Results Section */}
        {(currentStage === 'results' || currentStage === 'analysis' || currentStage === 'pdf') && (
          <LabResultsSection
            labResults={labResults}
            onUpdateResults={handleUpdateLabResults}
            onAddTest={handleAddTest}
            onDeleteTest={handleDeleteTest}
            onAnalyze={handleAnalyzeHealth}
            isLoading={isLoading}
            isExpanded={currentStage === 'results'}
          />
        )}

        {/* Organ Health Section */}
        {(currentStage === 'analysis' || currentStage === 'pdf') && organScores && (
          <OrganHealthSection
            organScores={organScores}
            onGeneratePDF={handleGeneratePDF}
            onEditResults={() => setCurrentStage('results')}
            onStartOver={handleStartOver}
            isLoading={isLoading}
            isExpanded={currentStage === 'analysis'}
          />
        )}

        {/* PDF Viewer Section */}
        {currentStage === 'pdf' && pdfData && (
          <PDFViewerSection
            pdfData={pdfData}
            onStartOver={handleStartOver}
          />
        )}
      </main>

      <Footer />
    </div>
  );
}

export default App;
