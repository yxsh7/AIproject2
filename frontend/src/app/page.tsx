export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-16">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold text-gray-900 mb-4">
            DevMetrics <span className="text-blue-600">AI</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Engineering Intelligence Platform
          </p>
          <p className="text-lg text-gray-500 max-w-2xl mx-auto">
            AI-powered productivity analytics that understands the complexity of engineering work.
            Not just lines of code, but real impact.
          </p>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="text-3xl mb-4">🧠</div>
            <h3 className="text-xl font-semibold mb-2">AI-Powered Analysis</h3>
            <p className="text-gray-600">
              Claude and GPT-4 analyze code complexity, work type, and impact - not just lines changed.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="text-3xl mb-4">📊</div>
            <h3 className="text-xl font-semibold mb-2">Multi-Dimensional Scoring</h3>
            <p className="text-gray-600">
              Role-based evaluation covering code quality, complexity, impact, and collaboration.
            </p>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="text-3xl mb-4">🔗</div>
            <h3 className="text-xl font-semibold mb-2">GitHub + Jira Integration</h3>
            <p className="text-gray-600">
              Unified view of all work - code, research, documentation, and more.
            </p>
          </div>
        </div>

        {/* Status */}
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold mb-4">Project Status</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="font-medium">Database Models</span>
              <span className="text-green-600 font-semibold">✓ Complete</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="font-medium">Backend API</span>
              <span className="text-yellow-600 font-semibold">⚡ In Progress</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="font-medium">AI Agents</span>
              <span className="text-gray-400 font-semibold">⏳ Pending</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="font-medium">Frontend Dashboard</span>
              <span className="text-yellow-600 font-semibold">⚡ In Progress</span>
            </div>
          </div>

          <div className="mt-8 pt-6 border-t">
            <h3 className="font-semibold mb-2">Quick Links</h3>
            <div className="space-y-2">
              <a href="/dashboard" className="block text-blue-600 hover:underline">
                → Developer Dashboard (Coming Soon)
              </a>
              <a href="/manager" className="block text-blue-600 hover:underline">
                → Manager Dashboard (Coming Soon)
              </a>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noopener noreferrer"
                className="block text-blue-600 hover:underline"
              >
                → API Documentation
              </a>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-16 text-gray-500">
          <p>Built with FastAPI, Next.js, LangChain, and Claude AI</p>
        </div>
      </div>
    </main>
  );
}
