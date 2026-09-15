import React from 'react';

interface CardProps {
  title: string;
  value: string;
  valueColor?: string;
  children?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ title, value, valueColor = 'text-white', children }) => {
  return (
    <div className="bg-[#161b22] border border-[#30363d] p-6 rounded-2xl shadow-sm">
      <p className="text-xs font-semibold text-gray-400 uppercase">{title}</p>
      <h3 className={`text-2xl font-bold mt-2 ${valueColor}`}>{value}</h3>
      {children}
    </div>
  );
};