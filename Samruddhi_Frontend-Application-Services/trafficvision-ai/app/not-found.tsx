import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-[#0d1117] text-white space-y-4">
      <h1 className="text-6xl font-bold text-[#1f6feb]">404</h1>
      <h2 className="text-xl font-semibold text-gray-200">Page Not Found</h2>
      <p className="text-sm text-gray-400">The route you are looking for does not exist in TrafficVision AI.</p>
      <Link 
        href="/dashboard" 
        className="px-5 py-2.5 bg-[#1f6feb] hover:bg-[#388bfd] rounded-xl text-sm font-semibold transition shadow-md"
      >
        Return to Dashboard
      </Link>
    </div>
  );
}
