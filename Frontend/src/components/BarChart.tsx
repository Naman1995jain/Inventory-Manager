import React from 'react';

interface BarChartProps {
  data: { label: string; value: number }[];
  height?: number;
}

// This component renders a donut / pie chart using SVG stroke-dasharray.
// It keeps the same prop shape as the original BarChart so existing imports don't need to change.
export default function BarChart({ data, height = 180 }: BarChartProps) {
  if (!data || data.length === 0) return <div className="text-sm text-gray-500">No data</div>;

  const total = data.reduce((s, d) => s + (d.value || 0), 0);
  if (total === 0) return <div className="text-sm text-gray-500">No data</div>;

  const radius = 60;
  const stroke = 28; // donut thickness
  const circumference = 2 * Math.PI * radius;

  // Colors to cycle through for slices
  const colors = [
    '#6366F1', // indigo-500
    '#06B6D4', // cyan-400
    '#34D399', // green-400
    '#F59E0B', // amber-500
    '#EF4444', // red-500
    '#A78BFA', // purple-300
    '#60A5FA', // blue-400
    '#F97316'
  ];

  let cumulative = 0;

  return (
    <div className="w-full flex flex-col lg:flex-row items-center gap-6">
      <div className="flex items-center justify-center">
        <svg width={radius * 2 + stroke} height={radius * 2 + stroke} viewBox={`0 0 ${radius * 2 + stroke} ${radius * 2 + stroke}`}>
          <g transform={`translate(${(stroke / 2) + radius}, ${(stroke / 2) + radius}) rotate(-90)`}>
            {data.map((d, i) => {
              const value = Math.max(0, d.value || 0);
              const len = (value / total) * circumference;
              const dashArray = `${len} ${circumference - len}`;
              const dashOffset = circumference - cumulative;
              cumulative += len;
              return (
                <circle
                  key={i}
                  r={radius}
                  cx={0}
                  cy={0}
                  fill="transparent"
                  stroke={colors[i % colors.length]}
                  strokeWidth={stroke}
                  strokeDasharray={dashArray}
                  strokeDashoffset={dashOffset}
                  style={{ transition: 'stroke-dasharray 600ms ease, stroke-dashoffset 600ms ease' }}
                />
              );
            })}
            {/* center label */}
            <g transform="rotate(90)">
              <text x="0" y="6" textAnchor="middle" className="text-sm font-semibold fill-current text-gray-900" style={{ fontSize: 14 }}>
                {total}
              </text>
              <text x="0" y="24" textAnchor="middle" className="text-xs fill-current text-gray-500" style={{ fontSize: 11 }}>
                total qty
              </text>
            </g>
          </g>
        </svg>
      </div>

      <div className="flex-1">
        <ul className="space-y-2">
          {data.map((d, i) => {
            const pct = ((d.value / total) * 100).toFixed(1);
            return (
              <li key={i} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <span className="inline-block w-3 h-3 rounded" style={{ background: colors[i % colors.length] }} />
                  <div className="text-sm text-gray-700 truncate max-w-[160px]">{d.label}</div>
                </div>
                <div className="text-sm text-gray-900 font-medium">{pct}%</div>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
