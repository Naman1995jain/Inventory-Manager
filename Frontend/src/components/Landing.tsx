import Link from 'next/link';
import Image from 'next/image';
import heroIllustration from '../public/images/illustraion.jpg';

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-white to-gray-50">
      {/* Hero Section */}
      <div className="container mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h1 className="text-4xl sm:text-6xl font-extrabold text-gray-900 leading-tight mb-6">
            Welcome to Our Platform
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Discover amazing books and manage your inventory efficiently — all in one place.
          </p>
        </div>

        {/* Two Main Sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 max-w-6xl mx-auto">
          
          {/* Book Collection Section */}
          <div className="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-shadow">
            <div className="text-center">
              <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-indigo-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                  <path fillRule="evenodd" d="M4 4a2 2 0 00-2 2v8a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2H4zm0 2h12v8H4V6z" clipRule="evenodd"/>
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Book Collection</h2>
              <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                Explore hundreds of carefully curated books across different genres. From fiction to poetry, 
                historical novels to contemporary works — find your next favorite read.
              </p>
              
              <div className="space-y-3 mb-6 text-sm text-gray-500">
                <div className="flex items-center justify-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  No account needed
                </div>
                <div className="flex items-center justify-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Instant access to full collection
                </div>
                <div className="flex items-center justify-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Detailed book information & reviews
                </div>
              </div>

              <Link
                href="/books"
                className="inline-flex items-center px-8 py-4 rounded-md bg-indigo-600 text-white font-medium shadow-md hover:bg-indigo-700 transition text-lg"
              >
                Browse Books
                <svg className="ml-2 w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd"/>
                </svg>
              </Link>
            </div>
          </div>

          {/* Inventory Management Section */}
          <div className="bg-white rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-shadow">
            <div className="text-center">
              <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-emerald-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M5 2a1 1 0 011 1v1h1a1 1 0 010 2H6v1a1 1 0 01-2 0V6H3a1 1 0 010-2h1V3a1 1 0 011-1zm0 10a1 1 0 011 1v1h1a1 1 0 110 2H6v1a1 1 0 11-2 0v-1H3a1 1 0 110-2h1v-1a1 1 0 011-1zM12 2a1 1 0 01.967.744L14.146 7.2 17.5 9.134a1 1 0 010 1.732L14.146 12.8l-1.179 4.456a1 1 0 01-1.806.152L9.5 14.866l-1.661 2.542a1 1 0 01-1.806-.152L4.854 12.8 1.5 10.866a1 1 0 010-1.732L4.854 7.2l1.179-4.456A1 1 0 017 2h5z" clipRule="evenodd"/>
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-gray-900 mb-4">Inventory Management</h2>
              <p className="text-gray-600 mb-6 text-lg leading-relaxed">
                Keep stock accurate, move products between warehouses, and get the insights you need — 
                without the complexity. Built for small teams and solo operators.
              </p>
              
              <div className="space-y-3 mb-6 text-sm text-gray-500">
                <div className="flex items-center justify-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Secure authentication & role-based access
                </div>
                <div className="flex items-center justify-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Multi-warehouse stock management
                </div>
                <div className="flex items-center justify-center">
                  <span className="w-2 h-2 bg-green-500 rounded-full mr-2"></span>
                  Detailed analytics & audit logs
                </div>
              </div>

              <div className="flex items-center justify-center gap-3">
                <Link
                  href="/login"
                  className="inline-flex items-center px-6 py-3 rounded-md bg-emerald-600 text-white font-medium shadow-md hover:bg-emerald-700 transition"
                >
                  Sign In
                </Link>
                <Link
                  href="/register"
                  className="inline-flex items-center px-6 py-3 rounded-md bg-white border border-gray-200 text-gray-700 font-medium hover:bg-gray-50 transition"
                >
                  Register
                </Link>
              </div>
            </div>
          </div>
        </div>
        </div>

      {/* Features Section */}
      <div className="bg-gray-50 py-16">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Why Choose Our Platform?</h2>
            <p className="text-gray-600 text-lg">Everything you need in one convenient location</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Easy to Use</h3>
              <p className="text-gray-600">Intuitive interface designed for both casual browsers and professional managers</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Secure & Reliable</h3>
              <p className="text-gray-600">Enterprise-grade security with data protection and reliable uptime</p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd"/>
                </svg>
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Fast & Efficient</h3>
              <p className="text-gray-600">Optimized performance with quick loading times and responsive design</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
