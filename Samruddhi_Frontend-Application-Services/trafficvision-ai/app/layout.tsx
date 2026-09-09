import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'TrafficVision AI',
  description: 'Smart Traffic Prediction & Congestion Management System',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-[#0d1117] text-white font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
