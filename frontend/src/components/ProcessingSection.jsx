import { motion } from 'framer-motion';
import { Upload, FileSearch, Brain, CheckCircle } from 'lucide-react';

const ProcessingSection = ({ stage }) => {
  const stages = [
    { id: 'upload', label: 'Uploading File', icon: Upload },
    { id: 'extraction', label: 'Extracting Text', icon: FileSearch },
    { id: 'analysis', label: 'Analyzing with AI', icon: Brain },
    { id: 'completed', label: 'Complete', icon: CheckCircle },
  ];

  const currentStageIndex = stages.findIndex(s => s.id === stage);

  return (
    <div className="max-w-4xl mx-auto">
      <div className="card">
        <h2 className="text-2xl font-bold text-gray-900 mb-8 text-center">
          Processing Your Report
        </h2>

        <div className="space-y-6">
          {stages.map((stageItem, index) => {
            const Icon = stageItem.icon;
            const isCompleted = index < currentStageIndex;
            const isCurrent = index === currentStageIndex;
            const isPending = index > currentStageIndex;

            return (
              <div key={stageItem.id} className="flex items-center gap-4">
                <div
                  className={`
                    w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0
                    transition-all duration-300
                    ${isCompleted ? 'bg-green-500' : ''}
                    ${isCurrent ? 'bg-primary' : ''}
                    ${isPending ? 'bg-gray-200' : ''}
                  `}
                >
                  {isCurrent ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                    >
                      <Icon className="w-6 h-6 text-white" />
                    </motion.div>
                  ) : (
                    <Icon
                      className={`w-6 h-6 ${
                        isCompleted || isCurrent ? 'text-white' : 'text-gray-400'
                      }`}
                    />
                  )}
                </div>

                <div className="flex-1">
                  <p
                    className={`font-medium ${
                      isCurrent ? 'text-primary' : isCompleted ? 'text-green-600' : 'text-gray-400'
                    }`}
                  >
                    {stageItem.label}
                  </p>
                  {isCurrent && (
                    <motion.div
                      className="mt-2 h-1 bg-primary rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: '100%' }}
                      transition={{ duration: 2, repeat: Infinity }}
                    />
                  )}
                </div>

                {isCompleted && (
                  <CheckCircle className="w-6 h-6 text-green-500" />
                )}
              </div>
            );
          })}
        </div>

        <div className="mt-8 text-center text-sm text-gray-600">
          <p>Please wait while we process your report...</p>
        </div>
      </div>
    </div>
  );
};

export default ProcessingSection;
