// ============================================================================
// frontend/src/components/watchlist/AgeProgression.jsx
// ============================================================================

import React, { useState } from 'react';
import { Upload, Calendar, User } from 'lucide-react';
import Card from '../common/Card';
import Button from '../common/Button';

export default function AgeProgression({ person }) {
  const [selectedImage, setSelectedImage] = useState(null);
  const [currentAge, setCurrentAge] = useState(person?.age || 10);
  const [targetAges, setTargetAges] = useState([15, 20, 25, 30]);
  const [progressedImages, setProgressedImages] = useState({});
  const [processing, setProcessing] = useState(false);

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setSelectedImage(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const generateAgeProgression = async () => {
    setProcessing(true);
    
    // Simulate age progression generation
    setTimeout(() => {
      const simulated = {};
      targetAges.forEach(age => {
        simulated[age] = selectedImage; // In real implementation, this would be the progressed image
      });
      setProgressedImages(simulated);
      setProcessing(false);
    }, 2000);
  };

  return (
    <div className="space-y-6">
      {/* Info Card */}
      <Card>
        <div className="flex items-start space-x-4">
          <div className="p-3 bg-blue-100 rounded-lg">
            <User className="w-6 h-6 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Age Progression</h3>
            <p className="text-sm text-gray-500 mt-1">
              Generate age-progressed images for synthetic missing persons.
              This helps identify how they might look at different ages.
            </p>
          </div>
        </div>
      </Card>

      {/* Upload Section */}
      <Card title="Upload Reference Image">
        <div className="space-y-4">
          <div className="flex items-center justify-center w-full">
            <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
              {selectedImage ? (
                <img
                  src={selectedImage}
                  alt="Selected"
                  className="h-full object-contain"
                />
              ) : (
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload className="w-12 h-12 text-gray-400 mb-3" />
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-gray-500">PNG, JPG (MAX. 5MB)</p>
                </div>
              )}
              <input
                type="file"
                className="hidden"
                accept="image/*"
                onChange={handleImageUpload}
              />
            </label>
          </div>

          {/* Age Configuration */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Current Age
              </label>
              <input
                type="number"
                min="1"
                max="100"
                value={currentAge}
                onChange={(e) => setCurrentAge(parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Target Ages (comma-separated)
              </label>
              <input
                type="text"
                value={targetAges.join(', ')}
                onChange={(e) => setTargetAges(e.target.value.split(',').map(a => parseInt(a.trim())).filter(a => !isNaN(a)))}
                placeholder="15, 20, 25, 30"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <Button
            variant="primary"
            onClick={generateAgeProgression}
            disabled={!selectedImage || processing}
            className="w-full"
          >
            {processing ? 'Generating...' : 'Generate Age Progression'}
          </Button>
        </div>
      </Card>

      {/* Results */}
      {Object.keys(progressedImages).length > 0 && (
        <Card title="Age-Progressed Images">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {targetAges.map((age) => (
              <div key={age} className="space-y-2">
                <div className="aspect-square bg-gray-100 rounded-lg overflow-hidden">
                  {progressedImages[age] ? (
                    <img
                      src={progressedImages[age]}
                      alt={`Age ${age}`}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-gray-400">
                      No image
                    </div>
                  )}
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium text-gray-900">Age {age}</p>
                  <p className="text-xs text-gray-500">
                    +{age - currentAge} years
                  </p>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-800">
              <strong>Note:</strong> Age progression is approximate and for demonstration only. 
              Actual appearance may vary significantly.
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}