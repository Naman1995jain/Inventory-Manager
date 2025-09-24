import Link from 'next/link';
import Image from 'next/image';
import heroIllustration from '../public/images/illustraion.jpg';

export default function Landing() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-b from-white to-gray-50">
      <div className="container mx-auto px-6 py-20">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          <div className="lg:col-span-6 text-center lg:text-left">
            <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 leading-tight mb-4">
              Inventory management that just works
            </h1>
            <p className="text-lg text-gray-600 mb-6 max-w-xl mx-auto lg:mx-0">
              Keep stock accurate, move products between warehouses, and get the insights you need — without the complexity. Built for small teams and solo operators.
            </p>

            <div className="flex items-center justify-center lg:justify-start gap-4">
              <Link
                href="/login"
                className="inline-flex items-center px-6 py-3 rounded-md bg-indigo-600 text-white font-medium shadow-md hover:bg-indigo-700 transition"
              >
                Get started
              </Link>

              <Link
                href="/register"
                className="inline-flex items-center px-6 py-3 rounded-md bg-white border border-gray-200 text-gray-700 font-medium hover:bg-gray-50 transition"
              >
                Create account
              </Link>
            </div>

            <p className="mt-6 text-sm text-gray-500 max-w-md mx-auto lg:mx-0">
              Secure authentication, role-based access and audit logs are available for production. Try the demo and explore the dashboard.
            </p>
          </div>

          <div className="lg:col-span-6 flex items-center justify-center relative">
            {/* Decorative gradient/background */}
            <div className="absolute -inset-3 bg-gradient-to-tr from-indigo-50 via-white to-indigo-50 rounded-3xl transform rotate-2 blur-xl opacity-60 pointer-events-none" />

            <div className="relative w-full max-w-md lg:max-w-xl">
              <div className="rounded-2xl shadow-2xl overflow-hidden transform transition-all motion-safe:animate-float">
                <Image
                  src={heroIllustration}
                  alt="Illustration showing inventory charts and a person with a laptop"
                  width={920}
                  height={720}
                  className="w-full h-auto object-cover"
                />
              </div>

              {/* Floating card */}
              <div className="absolute -bottom-6 left-4 sm:left-10 w-48 bg-white/90 backdrop-blur rounded-xl p-3 shadow-lg border border-white/60">
                <div className="text-sm font-semibold text-indigo-700">Inventory Overview</div>
                <div className="mt-2 text-xs text-gray-600">Products, transfers and stock levels in one place.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
