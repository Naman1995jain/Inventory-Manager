import React from 'react';

interface LineChartProps {
  data: number[];
  labels?: string[];
  width?: number;
  height?: number;
  stroke?: string;
  fill?: string;
}

export default function LineChart({ data, labels = [], width = 560, height = 160, stroke = '#6366f1', fill = 'rgba(99,102,241,0.12)' }: LineChartProps) {
  if (!data || data.length === 0) {
    return <div className="text-sm text-gray-500">No data</div>;
  }

  const max = Math.max(...data, 1);
  const min = Math.min(...data, 0);
  const points = data.map((d, i) => {
    const x = (i / (data.length - 1 || 1)) * width;
    const y = height - ((d - min) / (max - min || 1)) * height;
    return `${x},${y}`;
  }).join(' ');

  // Build area path
  const areaPath = `M0,${height} L${points.replace(/ /g, ' L ')} L${width},${height} Z`;

  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" className="rounded-md">
      <path d={areaPath} fill={fill} />
      <polyline points={points} fill="none" stroke={stroke} strokeWidth={2} strokeLinejoin="round" strokeLinecap="round" />
      {data.map((d, i) => {
        const x = (i / (data.length - 1 || 1)) * width;
        const y = height - ((d - min) / (max - min || 1)) * height;
        return <circle key={i} cx={x} cy={y} r={2.5} fill={stroke} />;
      })}
    </svg>
  );
}
