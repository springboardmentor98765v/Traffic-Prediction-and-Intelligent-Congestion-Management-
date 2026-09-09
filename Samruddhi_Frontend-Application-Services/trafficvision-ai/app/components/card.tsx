'use client';

interface CardProps {
  title: string;
  value: string;
  subtitle?: string;
  valueColor?: string;
}

export default function Card({ title, value, subtitle, valueColor = 'text-white' }: CardProps) {
  return (
    <div className="bg-[#121929] border border-slate-800/90 p-5 rounded-2xl flex-1 shadow-md">
      <p className="text-slate-400 text-xs font-bold mb-2">{title}</p>
      <h2 className={`text-3xl font-black ${valueColor}`}>
        {value} {subtitle && <span className="text-xl font-bold text-slate-300">{subtitle}</span>}
      </h2>
    </div>
  );
}
