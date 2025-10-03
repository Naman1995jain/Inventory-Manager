import React, { useState } from 'react';

interface BarChartProps {
  data: { label: string; value: number }[];
  height?: number;
}

export default function BarChart({ data, height = 180 }: BarChartProps) {
  const [showModal, setShowModal] = useState(false);
  const [hoverData, setHoverData] = useState<null | {
    label: string;
    value: number;
    percent: string;
  }>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [hoverIndex, setHoverIndex] = useState<number | null>(null);

  if (!data || data.length === 0) return <div className="text-sm text-gray-500">No data</div>;

  const total = data.reduce((s, d) => s + (d.value || 0), 0);
  if (total === 0) return <div className="text-sm text-gray-500">No data</div>;

  const radius = 60;
  const stroke = 28;
  const circumference = 2 * Math.PI * radius;

  const colors = [
    '#6366F1', '#06B6D4', '#34D399', '#F59E0B',
    '#EF4444', '#A78BFA', '#60A5FA', '#F97316'
  ];

  let cumulative = 0;

  return (
    <>
      <div className="w-full flex flex-col items-center gap-4">
        {/* Donut Chart */}
        <div className="flex items-center justify-center relative">
          <svg
            width={radius * 2 + stroke}
            height={radius * 2 + stroke}
            viewBox={`0 0 ${radius * 2 + stroke} ${radius * 2 + stroke}`}
            role="img"
            aria-label="Donut chart representing data values"
          >
            <g transform={`translate(${(stroke / 2) + radius}, ${(stroke / 2) + radius}) rotate(-90)`}>
              {data.map((d, i) => {
                const value = Math.max(0, d.value || 0);
                const len = (value / total) * circumference;
                const dashArray = `${len} ${circumference - len}`;
                const dashOffset = circumference - cumulative;

                // Calculate mid-angle of the arc
                const angle = (cumulative + len / 2) / circumference * 360;
                const rad = (angle * Math.PI) / 180;

                // If hovered, offset slightly in arc direction
                const offset = hoverIndex === i ? 6 : 0; // pop-out distance
                const dx = Math.cos(rad) * offset;
                const dy = Math.sin(rad) * offset;

                cumulative += len;
                const color = colors[i % colors.length];

                return (
                  <circle
                    key={i}
                    r={radius}
                    cx={dx}
                    cy={dy}
                    fill="transparent"
                    stroke={color}
                    strokeWidth={stroke}
                    strokeDasharray={dashArray}
                    strokeDashoffset={dashOffset}
                    style={{
                      transition: 'all 0.3s ease',
                      cursor: 'pointer',
                      filter: hoverIndex === i ? 'drop-shadow(0 2px 4px rgba(0,0,0,0.3))' : 'none',
                    }}
                    onMouseEnter={() => {
                      const percent = ((value / total) * 100).toFixed(1);
                      setHoverData({ label: d.label, value, percent });
                      setHoverIndex(i);
                    }}
                    onMouseLeave={() => {
                      setHoverData(null);
                      setHoverIndex(null);
                    }}
                    onMouseMove={(e) => {
                      setMousePos({ x: e.clientX, y: e.clientY });
                    }}
                  />
                );
              })}

              {/* Center Text */}
              <g transform="rotate(90)">
                <text x="0" y="6" textAnchor="middle" className="fill-gray-900" style={{ fontSize: 14 }}>
                  {total}
                </text>
                <text x="0" y="24" textAnchor="middle" className="fill-gray-500" style={{ fontSize: 11 }}>
                  total qty
                </text>
              </g>
            </g>
          </svg>
        </div>

        {/* View Details Button */}
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
        >
          View Details
        </button>
      </div>

      {/* Tooltip */}
      {hoverData && (
        <div
          className="fixed z-50 px-3 py-1.5 text-sm text-white bg-black bg-opacity-75 rounded shadow"
          style={{
            top: mousePos.y + 12,
            left: mousePos.x + 12,
            pointerEvents: 'none',
            transition: 'opacity 0.2s ease',
          }}
        >
          <div className="font-medium">{hoverData.label}</div>
          <div>{hoverData.value} ({hoverData.percent}%)</div>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-lg animate-fadeIn">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-800">Graph Details</h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-gray-500 hover:text-gray-700 text-xl"
              >
                &times;
              </button>
            </div>

            <ul className="divide-y divide-gray-200 max-h-64 overflow-y-auto">
              {data.map((d, i) => {
                const pct = ((d.value / total) * 100).toFixed(1);
                return (
                  <li key={i} className="py-2 flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded" style={{ background: colors[i % colors.length] }} />
                      <span className="text-gray-700 text-sm">{d.label}</span>
                    </div>
                    <div className="text-sm text-gray-800 font-medium">
                      {d.value} ({pct}%)
                    </div>
                  </li>
                );
              })}
            </ul>

            <div className="mt-4 text-right">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
