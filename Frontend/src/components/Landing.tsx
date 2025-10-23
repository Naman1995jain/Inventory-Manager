import Link from 'next/link';
import { useState, useEffect } from 'react';

export default function Landing() {
  const [scrollY, setScrollY] = useState(0);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
    
    const handleScroll = () => setScrollY(window.scrollY);
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('scroll', handleScroll);
    window.addEventListener('mousemove', handleMouseMove);

    return () => {
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, []);

  const parallaxOffset = scrollY * 0.5;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-hidden">
      {/* Animated Background Elements */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div 
          className="absolute w-96 h-96 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 transition-transform duration-1000 ease-out"
          style={{
            top: '10%',
            left: '10%',
            transform: `translate(${mousePosition.x * 0.02}px, ${mousePosition.y * 0.02}px)`,
            animation: 'blob 7s infinite'
          }}
        />
        <div 
          className="absolute w-96 h-96 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 transition-transform duration-1000 ease-out"
          style={{
            top: '50%',
            right: '10%',
            transform: `translate(${mousePosition.x * -0.015}px, ${mousePosition.y * 0.015}px)`,
            animation: 'blob 7s infinite 2s'
          }}
        />
        <div 
          className="absolute w-96 h-96 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 transition-transform duration-1000 ease-out"
          style={{
            bottom: '10%',
            left: '50%',
            transform: `translate(${mousePosition.x * 0.01}px, ${mousePosition.y * -0.01}px)`,
            animation: 'blob 7s infinite 4s'
          }}
        />
      </div>

      {/* Hero Section */}
      <div className="relative container mx-auto px-6 pt-20 pb-32">
        <div 
          className={`text-center mb-20 transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
          style={{ transform: `translateY(${parallaxOffset * 0.3}px)` }}
        >
          <div className="inline-block mb-6" style={{ animation: 'float 3s ease-in-out infinite' }}>
            <div className="px-4 py-2 rounded-full bg-gradient-to-r from-purple-500/20 to-pink-500/20 border border-purple-500/30 backdrop-blur-sm">
              <span className="text-purple-300 text-sm font-medium">✨ Your Gateway to Excellence</span>
            </div>
          </div>
          
          <h1 className="text-5xl sm:text-7xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 leading-tight mb-6">
            Welcome to Our Platform
          </h1>
          
          <p className="text-xl sm:text-2xl text-gray-300 max-w-3xl mx-auto mb-8">
            Discover amazing test book? ok and manage your inventory efficiently — all in one place.
          </p>

          <div className="flex items-center justify-center gap-2 text-sm text-gray-400">
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-green-400 rounded-full" style={{ animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' }}></div>
              <span>1000+ Books</span>
            </div>
            <span>•</span>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-blue-400 rounded-full" style={{ animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite 0.5s' }}></div>
              <span>Secure Access</span>
            </div>
            <span>•</span>
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 bg-purple-400 rounded-full" style={{ animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite 1s' }}></div>
              <span>Real-time Updates</span>
            </div>
          </div>
        </div>

        {/* Main Feature Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {/* Book Collection Card */}
          <div
            className={`group relative bg-gradient-to-br from-purple-900/50 to-blue-900/50 rounded-3xl p-8 backdrop-blur-xl border border-purple-500/20 hover:border-purple-500/40 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/20 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
            style={{ 
              transform: `translateY(${parallaxOffset * 0.1}px)`,
              transitionDelay: '200ms'
            }}
          >
            {/* Glow Effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-purple-500/0 via-purple-500/10 to-purple-500/0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            
            <div className="relative text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-6 transform group-hover:rotate-12 transition-transform duration-500 shadow-lg shadow-purple-500/50">
                <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M4 3a1 1 0 00-1 1v16a1 1 0 001 1h16a1 1 0 001-1V4a1 1 0 00-1-1H4zm1 2h14v14H5V5z"/>
                  <path d="M6 7h12v2H6V7zm0 4h12v2H6v-2zm0 4h8v2H6v-2z"/>
                </svg>
              </div>
              
              <h2 className="text-3xl font-bold text-white mb-4 group-hover:text-purple-300 transition-colors">
                Book Collection
              </h2>
              
              <p className="text-gray-300 mb-6 text-lg leading-relaxed">
                Explore hundreds of carefully curated books across different genres. From fiction to poetry, 
                historical novels to contemporary works — find your next favorite read.
              </p>
              
              <div className="space-y-3 mb-8">
                {['No account needed', 'Instant access to full collection', 'Detailed book information & reviews'].map((feature, idx) => (
                  <div 
                    key={idx}
                    className="flex items-center justify-center gap-2 text-gray-400 group-hover:text-purple-300 transition-colors"
                  >
                    <div className="w-2 h-2 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full" style={{ animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' }} />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>

              <Link 
                href="/books"
                className="relative inline-flex items-center gap-2 px-8 py-4 rounded-xl bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold shadow-lg shadow-purple-500/50 hover:shadow-purple-500/80 transition-all duration-300 hover:scale-110 group/btn overflow-hidden"
              >
                <span className="relative z-10 flex items-center gap-2">
                  Browse Books
                  <svg className="w-5 h-5 group-hover/btn:translate-x-1 transition-transform" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clipRule="evenodd"/>
                  </svg>
                </span>
                <div className="absolute inset-0 bg-gradient-to-r from-pink-600 to-purple-600 opacity-0 group-hover/btn:opacity-100 transition-opacity" />
              </Link>
            </div>
          </div>

          {/* Inventory Management Card */}
          <div
            className={`group relative bg-gradient-to-br from-blue-900/50 to-emerald-900/50 rounded-3xl p-8 backdrop-blur-xl border border-blue-500/20 hover:border-blue-500/40 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-blue-500/20 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-10'}`}
            style={{ 
              transform: `translateY(${parallaxOffset * 0.1}px)`,
              transitionDelay: '400ms'
            }}
          >
            {/* Glow Effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/0 via-blue-500/10 to-blue-500/0 rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            
            <div className="relative text-center">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-emerald-500 rounded-2xl flex items-center justify-center mx-auto mb-6 transform group-hover:rotate-12 transition-transform duration-500 shadow-lg shadow-blue-500/50">
                <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M4 3a1 1 0 00-1 1v3h14V4a1 1 0 00-1-1H4z"/>
                  <path d="M3 9v7a1 1 0 001 1h12a1 1 0 001-1V9H3zm3 2h2v3H6v-3zm4 0h2v3h-2v-3zm4 0h2v3h-2v-3z"/>
                </svg>
              </div>
              
              <h2 className="text-3xl font-bold text-white mb-4 group-hover:text-blue-300 transition-colors">
                Inventory Management
              </h2>
              
              <p className="text-gray-300 mb-6 text-lg leading-relaxed">
                Keep stock accurate, move products between warehouses, and get the insights you need — 
                without the complexity. Built for small teams and solo operators.
              </p>
              
              <div className="space-y-3 mb-8">
                {['Secure authentication & role-based access', 'Multi-warehouse stock management', 'Detailed analytics & audit logs'].map((feature, idx) => (
                  <div 
                    key={idx}
                    className="flex items-center justify-center gap-2 text-gray-400 group-hover:text-blue-300 transition-colors"
                  >
                    <div className="w-2 h-2 bg-gradient-to-r from-blue-400 to-emerald-400 rounded-full" style={{ animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' }} />
                    <span>{feature}</span>
                  </div>
                ))}
              </div>

              <div className="flex items-center justify-center gap-3">
                <Link 
                  href="/login"
                  className="relative inline-flex items-center px-6 py-3 rounded-xl bg-gradient-to-r from-blue-600 to-emerald-600 text-white font-semibold shadow-lg shadow-blue-500/50 hover:shadow-blue-500/80 transition-all duration-300 hover:scale-110 overflow-hidden group/btn"
                >
                  <span className="relative z-10">Sign In</span>
                  <div className="absolute inset-0 bg-gradient-to-r from-emerald-600 to-blue-600 opacity-0 group-hover/btn:opacity-100 transition-opacity" />
                </Link>
                
                <Link 
                  href="/register"
                  className="inline-flex items-center px-6 py-3 rounded-xl bg-white/10 backdrop-blur-sm border border-white/20 text-white font-semibold hover:bg-white/20 transition-all duration-300 hover:scale-110"
                >
                  Register
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="relative py-20 bg-black/20 backdrop-blur-sm border-y border-white/10">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400 mb-4">
              Why Choose Our Platform?
            </h2>
            <p className="text-gray-400 text-lg">Everything you need in one convenient location</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                icon: (
                  <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                ),
                title: 'Easy to Use',
                desc: 'Intuitive interface designed for both casual browsers and professional managers',
                color: 'from-blue-500 to-cyan-500'
              },
              {
                icon: (
                  <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                ),
                title: 'Secure & Reliable',
                desc: 'Enterprise-grade security with data protection and reliable uptime',
                color: 'from-emerald-500 to-green-500'
              },
              {
                icon: (
                  <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd"/>
                ),
                title: 'Fast & Efficient',
                desc: 'Optimized performance with quick loading times and responsive design',
                color: 'from-purple-500 to-pink-500'
              }
            ].map((feature, idx) => (
              <div 
                key={idx}
                className="group relative bg-white/5 backdrop-blur-sm rounded-2xl p-8 border border-white/10 hover:border-white/20 transition-all duration-500 hover:scale-105 hover:bg-white/10"
              >
                <div className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-xl flex items-center justify-center mx-auto mb-4 transform group-hover:rotate-12 transition-transform duration-500 shadow-lg`}>
                  <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
                    {feature.icon}
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
        }
        
        @keyframes float {
          0%, 100% { transform: translateY(0px); }
          50% { transform: translateY(-10px); }
        }
        
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: .5; }
        }
      `}</style>
    </div>
  );
}
