import { useState } from 'react';
import { Pencil, Trash2, Plus, ChevronDown, ChevronUp } from 'lucide-react';

const LabResultsSection = ({
  labResults,
  onUpdateResults,
  onAddTest,
  onDeleteTest,
  onAnalyze,
  isLoading,
  isExpanded
}) => {
  const [filter, setFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newTest, setNewTest] = useState({ test_name: '', value: '', unit: '' });
  const [expanded, setExpanded] = useState(isExpanded);

  const filteredResults = labResults.filter(test => {
    const matchesSearch = test.test_name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesFilter =
      filter === 'all' ||
      (filter === 'normal' && test.status === 'Normal') ||
      (filter === 'abnormal' && test.status !== 'Normal');
    return matchesSearch && matchesFilter;
  });

  const handleAddTest = async () => {
    if (newTest.test_name && newTest.value && newTest.unit) {
      await onAddTest({
        test_name: newTest.test_name,
        value: parseFloat(newTest.value),
        unit: newTest.unit
      });
      setNewTest({ test_name: '', value: '', unit: '' });
      setShowAddForm(false);
    }
  };

  const getStatusBadgeClass = (status) => {
    if (status === 'Normal') return 'badge-normal';
    if (status.includes('Critical')) return 'badge-critical';
    if (status.includes('High') || status.includes('Low')) return 'badge-high';
    return 'badge-low';
  };

  return (
    <div className="mb-8">
      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Lab Test Results</h2>
            <p className="text-sm text-gray-600 mt-1">
              {labResults.length} tests found • Review and edit as needed
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
            {/* Filters and Search */}
            <div className="flex flex-wrap gap-4 mb-6">
              <div className="flex gap-2">
                <button
                  onClick={() => setFilter('all')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filter === 'all'
                      ? 'bg-primary text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  All ({labResults.length})
                </button>
                <button
                  onClick={() => setFilter('normal')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filter === 'normal'
                      ? 'bg-green-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Normal ({labResults.filter(t => t.status === 'Normal').length})
                </button>
                <button
                  onClick={() => setFilter('abnormal')}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                    filter === 'abnormal'
                      ? 'bg-red-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Abnormal ({labResults.filter(t => t.status !== 'Normal').length})
                </button>
              </div>

              <input
                type="text"
                placeholder="Search tests..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="flex-1 min-w-[200px] px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
              />

              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="btn-secondary flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Add Test
              </button>
            </div>

            {/* Add Test Form */}
            {showAddForm && (
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-gray-900 mb-3">Add Manual Test</h3>
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <input
                    type="text"
                    placeholder="Test Name"
                    value={newTest.test_name}
                    onChange={(e) => setNewTest({ ...newTest, test_name: e.target.value })}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <input
                    type="number"
                    step="0.01"
                    placeholder="Value"
                    value={newTest.value}
                    onChange={(e) => setNewTest({ ...newTest, value: e.target.value })}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <input
                    type="text"
                    placeholder="Unit (e.g., mg/dL)"
                    value={newTest.unit}
                    onChange={(e) => setNewTest({ ...newTest, unit: e.target.value })}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                  />
                  <button
                    onClick={handleAddTest}
                    className="btn-primary"
                  >
                    Add Test
                  </button>
                </div>
              </div>
            )}

            {/* Results Table */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Test Name</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Value</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Unit</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Normal Range</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                    <th className="px-4 py-3 text-left text-sm font-semibold text-gray-900">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {filteredResults.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                        No tests found. Try adjusting your filters or add tests manually.
                      </td>
                    </tr>
                  ) : (
                    filteredResults.map((test) => (
                      <tr key={test.test_id} className="hover:bg-gray-50">
                        <td className="px-4 py-3 text-sm text-gray-900">{test.test_name}</td>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">{test.value}</td>
                        <td className="px-4 py-3 text-sm text-gray-600">{test.unit}</td>
                        <td className="px-4 py-3 text-sm text-gray-600">
                          {test.normal_range_min && test.normal_range_max
                            ? `${test.normal_range_min} - ${test.normal_range_max}`
                            : 'N/A'}
                        </td>
                        <td className="px-4 py-3">
                          <span className={`badge ${getStatusBadgeClass(test.status)}`}>
                            {test.status}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <button
                            onClick={() => onDeleteTest(test.test_id)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* Analyze Button */}
            {labResults.length > 0 && (
              <div className="mt-6 flex justify-center">
                <button
                  onClick={onAnalyze}
                  disabled={isLoading}
                  className="btn-primary text-lg px-8 py-4"
                >
                  {isLoading ? 'Analyzing...' : 'Analyze Organ Health →'}
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default LabResultsSection;
