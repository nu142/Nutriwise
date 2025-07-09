import React, { useState, useEffect } from 'react';
import './App.css';

const API_BASE_URL = 'https://92e8a57e-565c-476f-a61a-306ae44bc398.preview.emergentagent.com';

function App() {
  const [nutritionData, setNutritionData] = useState({
    food_name: '',
    serving_size: '1 serving',
    calories: '',
    total_fat: '',
    saturated_fat: '',
    trans_fat: '',
    cholesterol: '',
    sodium: '',
    total_carbs: '',
    dietary_fiber: '',
    total_sugars: '',
    added_sugars: '',
    protein: '',
    vitamin_d: '',
    calcium: '',
    iron: '',
    potassium: ''
  });

  const [results, setResults] = useState({
    simplification: null,
    healthGoal: null,
    dietCompatibility: null,
    warnings: null
  });

  const [currentHealthGoal, setCurrentHealthGoal] = useState('weight_loss');
  const [currentDietType, setCurrentDietType] = useState('keto');
  const [chatQuestion, setChatQuestion] = useState('');
  const [chatResponse, setChatResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isModelLoaded, setIsModelLoaded] = useState(false);

  const healthGoals = [
    { value: 'weight_loss', label: 'Weight Loss' },
    { value: 'muscle_gain', label: 'Muscle Gain' },
    { value: 'heart_health', label: 'Heart Health' },
    { value: 'diabetes_management', label: 'Diabetes Management' }
  ];

  const dietTypes = [
    { value: 'keto', label: 'Keto' },
    { value: 'vegan', label: 'Vegan' },
    { value: 'paleo', label: 'Paleo' },
    { value: 'mediterranean', label: 'Mediterranean' },
    { value: 'low_sodium', label: 'Low Sodium' }
  ];

  useEffect(() => {
    checkModelStatus();
  }, []);

  const checkModelStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/health`);
      const data = await response.json();
      setIsModelLoaded(data.models_loaded);
    } catch (error) {
      console.error('Error checking model status:', error);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNutritionData(prev => ({
      ...prev,
      [name]: value === '' ? '' : parseFloat(value) || 0
    }));
  };

  const processAllFunctionalities = async () => {
    if (!nutritionData.food_name || !nutritionData.calories) {
      alert('Please fill in at least the food name and calories');
      return;
    }

    setLoading(true);
    try {
      // Functionality 1: Simplification
      const simplificationResponse = await fetch(`${API_BASE_URL}/api/nutrition/simplify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(nutritionData)
      });
      const simplificationData = await simplificationResponse.json();

      // Functionality 2: Health Goal
      const healthGoalResponse = await fetch(`${API_BASE_URL}/api/nutrition/health-goal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nutrition_data: nutritionData,
          health_goal: currentHealthGoal
        })
      });
      const healthGoalData = await healthGoalResponse.json();

      // Functionality 3: Diet Compatibility
      const dietResponse = await fetch(`${API_BASE_URL}/api/nutrition/diet-compatibility`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nutrition_data: nutritionData,
          diet_type: currentDietType
        })
      });
      const dietData = await dietResponse.json();

      // Functionality 5: Warnings
      const warningsResponse = await fetch(`${API_BASE_URL}/api/nutrition/warnings`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(nutritionData)
      });
      const warningsData = await warningsResponse.json();

      setResults({
        simplification: simplificationData,
        healthGoal: healthGoalData,
        dietCompatibility: dietData,
        warnings: warningsData
      });

    } catch (error) {
      console.error('Error processing nutrition data:', error);
      alert('Error processing nutrition data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleChatQuestion = async () => {
    if (!chatQuestion.trim() || !nutritionData.food_name) {
      alert('Please enter a question and nutrition data');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/nutrition/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nutrition_data: nutritionData,
          question: chatQuestion,
          context: results.simplification?.simplified_explanation || ''
        })
      });
      const data = await response.json();
      setChatResponse(data);
    } catch (error) {
      console.error('Error with chat:', error);
      alert('Error processing your question. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const clearAll = () => {
    setNutritionData({
      food_name: '',
      serving_size: '1 serving',
      calories: '',
      total_fat: '',
      saturated_fat: '',
      trans_fat: '',
      cholesterol: '',
      sodium: '',
      total_carbs: '',
      dietary_fiber: '',
      total_sugars: '',
      added_sugars: '',
      protein: '',
      vitamin_d: '',
      calcium: '',
      iron: '',
      potassium: ''
    });
    setResults({
      simplification: null,
      healthGoal: null,
      dietCompatibility: null,
      warnings: null
    });
    setChatResponse(null);
    setChatQuestion('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50">
      {/* Header */}
      <div className="bg-white shadow-lg border-b">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">🥗 Smart Nutrition Analyzer</h1>
              <p className="text-gray-600 mt-1">AI-powered nutrition analysis with 5 smart functionalities</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                isModelLoaded ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
              }`}>
                {isModelLoaded ? '✅ AI Ready' : '⏳ Loading AI...'}
              </div>
              <button
                onClick={clearAll}
                className="bg-red-500 text-white px-4 py-2 rounded-lg hover:bg-red-600 transition-colors"
              >
                Clear All
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Input Section */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">📊 Nutrition Input</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Food Name</label>
                  <input
                    type="text"
                    name="food_name"
                    value={nutritionData.food_name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., Greek Yogurt"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Serving Size</label>
                  <input
                    type="text"
                    name="serving_size"
                    value={nutritionData.serving_size}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g., 1 cup"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Calories</label>
                    <input
                      type="number"
                      name="calories"
                      value={nutritionData.calories}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Total Fat (g)</label>
                    <input
                      type="number"
                      name="total_fat"
                      value={nutritionData.total_fat}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="0"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Saturated Fat (g)</label>
                    <input
                      type="number"
                      name="saturated_fat"
                      value={nutritionData.saturated_fat}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Cholesterol (mg)</label>
                    <input
                      type="number"
                      name="cholesterol"
                      value={nutritionData.cholesterol}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="0"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Sodium (mg)</label>
                    <input
                      type="number"
                      name="sodium"
                      value={nutritionData.sodium}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Total Carbs (g)</label>
                    <input
                      type="number"
                      name="total_carbs"
                      value={nutritionData.total_carbs}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="0"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Dietary Fiber (g)</label>
                    <input
                      type="number"
                      name="dietary_fiber"
                      value={nutritionData.dietary_fiber}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="0"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Added Sugars (g)</label>
                    <input
                      type="number"
                      name="added_sugars"
                      value={nutritionData.added_sugars}
                      onChange={handleInputChange}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="0"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Protein (g)</label>
                  <input
                    type="number"
                    name="protein"
                    value={nutritionData.protein}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="0"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Health Goal</label>
                    <select
                      value={currentHealthGoal}
                      onChange={(e) => setCurrentHealthGoal(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      {healthGoals.map(goal => (
                        <option key={goal.value} value={goal.value}>{goal.label}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Diet Type</label>
                    <select
                      value={currentDietType}
                      onChange={(e) => setCurrentDietType(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      {dietTypes.map(diet => (
                        <option key={diet.value} value={diet.value}>{diet.label}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <button
                  onClick={processAllFunctionalities}
                  disabled={loading || !isModelLoaded}
                  className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-lg font-semibold hover:from-blue-600 hover:to-purple-700 transition-all disabled:opacity-50"
                >
                  {loading ? '🔄 Processing...' : '🚀 Analyze Nutrition'}
                </button>
              </div>
            </div>

            {/* Chat Section */}
            <div className="bg-white rounded-xl shadow-lg p-6 mt-6">
              <h2 className="text-xl font-semibold mb-4 text-gray-900">💬 Ask Questions</h2>
              <div className="space-y-4">
                <textarea
                  value={chatQuestion}
                  onChange={(e) => setChatQuestion(e.target.value)}
                  placeholder="Ask anything about this nutrition info..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent h-20 resize-none"
                />
                <button
                  onClick={handleChatQuestion}
                  disabled={loading || !chatQuestion.trim()}
                  className="w-full bg-green-500 text-white py-2 rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50"
                >
                  {loading ? '🤔 Thinking...' : 'Ask Question'}
                </button>
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div className="lg:col-span-2">
            <div className="space-y-6">
              {/* Simplification Results */}
              {results.simplification && (
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h3 className="text-lg font-semibold mb-4 text-blue-900">📝 Simplified Explanation</h3>
                  <div className="bg-blue-50 rounded-lg p-4 mb-4">
                    <p className="text-gray-700">{results.simplification.simplified_explanation}</p>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(results.simplification.daily_value_percentages).map(([nutrient, percentage]) => (
                      <div key={nutrient} className="text-center">
                        <div className="text-2xl font-bold text-blue-600">{percentage}%</div>
                        <div className="text-sm text-gray-600 capitalize">{nutrient.replace('_', ' ')}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Health Goal Results */}
              {results.healthGoal && (
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h3 className="text-lg font-semibold mb-4 text-green-900">🎯 Health Goal Analysis</h3>
                  <div className="bg-green-50 rounded-lg p-4 mb-4">
                    <p className="text-gray-700">{results.healthGoal.suitability_verdict}</p>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">{results.healthGoal.suitability_score}/100</div>
                        <div className="text-sm text-gray-600">Suitability Score</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-semibold text-green-700">{results.healthGoal.recommendation}</div>
                        <div className="text-sm text-gray-600">Recommendation</div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Diet Compatibility Results */}
              {results.dietCompatibility && (
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h3 className="text-lg font-semibold mb-4 text-purple-900">🥗 Diet Compatibility</h3>
                  <div className="bg-purple-50 rounded-lg p-4 mb-4">
                    <p className="text-gray-700">{results.dietCompatibility.compatibility_explanation}</p>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-purple-600">{results.dietCompatibility.compatibility_score}/100</div>
                        <div className="text-sm text-gray-600">Compatibility Score</div>
                      </div>
                      <div className="text-center">
                        <div className={`px-4 py-2 rounded-full text-sm font-medium ${
                          results.dietCompatibility.is_compatible 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {results.dietCompatibility.is_compatible ? '✅ Compatible' : '❌ Not Compatible'}
                        </div>
                      </div>
                    </div>
                  </div>
                  {results.dietCompatibility.specific_concerns.length > 0 && (
                    <div className="mt-4">
                      <h4 className="font-medium text-gray-900 mb-2">Specific Concerns:</h4>
                      <ul className="list-disc list-inside text-red-600 space-y-1">
                        {results.dietCompatibility.specific_concerns.map((concern, index) => (
                          <li key={index}>{concern}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* Warnings and Suggestions */}
              {results.warnings && (
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h3 className="text-lg font-semibold mb-4 text-red-900">⚠️ Health Warnings & Suggestions</h3>
                  <div className="bg-red-50 rounded-lg p-4 mb-4">
                    <p className="text-gray-700">{results.warnings.ai_analysis}</p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-medium text-red-800 mb-2">Health Warnings:</h4>
                      <div className="space-y-2">
                        {results.warnings.health_warnings.map((warning, index) => (
                          <div key={index} className="bg-red-100 text-red-800 p-2 rounded text-sm">
                            {warning}
                          </div>
                        ))}
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-medium text-green-800 mb-2">Alternative Suggestions:</h4>
                      <div className="space-y-2">
                        {results.warnings.alternative_suggestions.map((suggestion, index) => (
                          <div key={index} className="bg-green-100 text-green-800 p-2 rounded text-sm">
                            {suggestion}
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4 text-center">
                    <div className="inline-flex items-center space-x-2">
                      <span className="text-gray-600">Overall Health Score:</span>
                      <span className="text-2xl font-bold text-orange-600">{results.warnings.overall_health_score}/100</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Chat Response */}
              {chatResponse && (
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h3 className="text-lg font-semibold mb-4 text-indigo-900">💬 Assistant Response</h3>
                  <div className="bg-indigo-50 rounded-lg p-4 mb-4">
                    <p className="text-gray-700 font-medium mb-2">Q: {chatResponse.question}</p>
                    <p className="text-gray-700">A: {chatResponse.answer}</p>
                  </div>
                  {chatResponse.follow_up_suggestions && (
                    <div>
                      <h4 className="font-medium text-gray-900 mb-2">Follow-up Questions:</h4>
                      <div className="space-y-1">
                        {chatResponse.follow_up_suggestions.map((suggestion, index) => (
                          <button
                            key={index}
                            onClick={() => setChatQuestion(suggestion)}
                            className="block w-full text-left px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded text-sm text-gray-700"
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;