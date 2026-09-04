import { useState } from 'react';
import { Heart, Droplet, Activity, AlertCircle, ChevronDown, ChevronUp, FileDown } from 'lucide-react';

const OrganHealthSection = ({
  organScores,
  onGeneratePDF,
  onEditResults,
  onStartOver,
  isLoading,
  isExpanded
}) => {
  const [expanded, setExpanded] = useState(isExpanded);

  const getScoreColor = (score) => {
    if (score >= 90) return 'text-health-excellent';
    if (score >= 70) return 'text-health-good';
    if (score >= 50) return 'text-health-concerning';
    return 'text-health-critical';
  };

  const getScoreBgColor = (score) => {
    if (score >= 90) return 'bg-health-excellent/10 border-health-excellent';
    if (score >= 70) return 'bg-health-good/10 border-health-good';
    if (score >= 50) return 'bg-health-concerning/10 border-health-concerning';
    return 'bg-health-critical/10 border-health-critical';
  };

  return (
    <div className="mb-8">
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Organ Health Analysis</h2>
            <p className="text-sm text-gray-600 mt-1">
              Based on your lab test results
            </p>
          </div>
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-2 text-primary hover:text-primary-dark"
          >
            {expanded ? <ChevronUp /> : <ChevronDown />}
          </button>
        </div>

        {expanded && (
          <>
            {/* Overall Health Score */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-8 mb-8 text-center">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Overall Health Score</h3>
              <div className={`text-6xl font-bold mb-4 ${getScoreColor(organScores.overall_health_score)}`}>
                {organScores.overall_health_score}
                <span className="text-2xl text-gray-500">/100</span>
              </div>
              <p className="text-gray-600">
                Based on analysis of {organScores.organ_scores.length} organ systems
              </p>
            </div>

            {/* Organ Cards Grid */}
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              {organScores.organ_scores.map((organ) => (
                <div
                  key={organ.organ_id}
                  className={`border-2 rounded-xl p-6 ${getScoreBgColor(organ.health_score)}`}
                >
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-gray-900">{organ.organ_name}</h3>
                      <p className="text-sm text-gray-600 mt-1">{organ.description}</p>
                    </div>
                    <div className={`text-3xl font-bold ${getScoreColor(organ.health_score)}`}>
                      {organ.health_score}
                    </div>
                  </div>

                  <div className="flex items-center gap-4 mb-4">
                    <span className={`badge ${
                      organ.status === 'Excellent' ? 'badge-normal' :
                      organ.status === 'Good' ? 'bg-yellow-100 text-yellow-800' :
                      organ.status === 'Attention Needed' ? 'bg-orange-100 text-orange-800' :
                      'badge-critical'
                    }`}>
                      {organ.status}
                    </span>
                    <span className="text-sm text-gray-600">
                      {organ.test_count} tests • {organ.abnormal_test_count} abnormal
                    </span>
                  </div>

                  {/* Related Tests */}
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Related Tests:</h4>
                    <div className="space-y-2">
                      {organ.related_tests.slice(0, 3).map((test, idx) => (
                        <div key={idx} className="flex items-center justify-between text-sm">
                          <span className="text-gray-700">{test.test_name}</span>
                          <span className="font-medium">
                            {test.value} {test.unit}
                            <span className={`ml-2 text-xs ${
                              test.status === 'Normal' ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {test.status}
                            </span>
                          </span>
                        </div>
                      ))}
                      {organ.related_tests.length > 3 && (
                        <p className="text-xs text-gray-500">
                          +{organ.related_tests.length - 3} more tests
                        </p>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Recommendations */}
            {organScores.recommendations && organScores.recommendations.length > 0 && (
              <div className="mb-8">
                <h3 className="text-xl font-bold text-gray-900 mb-4">Health Recommendations</h3>
                <div className="space-y-4">
                  {organScores.recommendations.map((rec) => (
                    <div
                      key={rec.recommendation_id}
                      className="bg-yellow-50 border-l-4 border-yellow-400 rounded-lg p-4"
                    >
                      <div className="flex items-start gap-3">
                        <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                          <p className="font-medium text-gray-900 mb-1">
                            {rec.organ_name}: {rec.text}
                          </p>
                          <div className="flex items-center gap-2 text-xs text-gray-600">
                            <span className="badge bg-yellow-100 text-yellow-800">
                              {rec.category.replace('_', ' ')}
                            </span>
                            <span className="badge bg-red-100 text-red-800">
                              {rec.severity}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex flex-wrap gap-4 justify-center">
              <button
                onClick={onGeneratePDF}
                disabled={isLoading}
                className="btn-primary text-lg px-8 py-4 flex items-center gap-2"
              >
                <FileDown className="w-5 h-5" />
                {isLoading ? 'Generating PDF...' : 'Generate PDF Report'}
              </button>
              <button
                onClick={onEditResults}
                className="btn-secondary"
              >
                Edit Results
              </button>
              <button
                onClick={onStartOver}
                className="px-6 py-3 text-gray-700 hover:bg-gray-100 rounded-lg font-semibold transition-colors"
              >
                Start Over
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default OrganHealthSection;
