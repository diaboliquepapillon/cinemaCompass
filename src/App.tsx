function App() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-cine-dark via-cine-darker to-cine-card">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-cine-purple mb-4">
            🎬 CinemaCompass
          </h1>
          <p className="text-xl text-gray-300 mb-8">
            Hybrid Movie Recommendation System
          </p>
          
          <div className="max-w-2xl mx-auto bg-cine-card rounded-lg p-8 shadow-2xl">
            <h2 className="text-2xl font-semibold text-white mb-6">
              Welcome to CinemaCompass
            </h2>
            
            <p className="text-gray-400 mb-6">
              This is the React frontend for the CinemaCompass movie recommendation system.
            </p>
            
            <div className="flex flex-col gap-4">
              <div className="bg-cine-darker rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-2">
                  Features
                </h3>
                <ul className="text-gray-300 space-y-2 text-left">
                  <li>• Hybrid recommendation system (Content-based + Collaborative filtering)</li>
                  <li>• Rich metadata utilization (genre, director, cast, tags)</li>
                  <li>• Personalized explanations</li>
                  <li>• Evaluation metrics (Precision@K, NDCG, etc.)</li>
                </ul>
              </div>
              
              <div className="bg-cine-darker rounded-lg p-4">
                <h3 className="text-lg font-semibold text-white mb-2">
                  Try the Recommendation System
                </h3>
                <p className="text-gray-300 mb-4">
                  For the full recommendation system with interactive UI, run the Streamlit app:
                </p>
                <code className="block bg-black text-green-400 p-3 rounded text-sm text-left">
                  streamlit run app.py
                </code>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
