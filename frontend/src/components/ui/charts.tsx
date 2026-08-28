'use client';

import { useMemo } from 'react';

interface BarChartProps {
  data: { label: string; value: number; color?: string }[];
  maxValue?: number;
  height?: number;
  showValues?: boolean;
  className?: string;
}

export function BarChart({
  data,
  maxValue: customMax,
  height = 200,
  showValues = true,
  className = ''
}: BarChartProps) {
  const maxValue = customMax || Math.max(...data.map(d => d.value), 1);

  return (
    <div className={`flex items-end gap-2 ${className}`} style={{ height }}>
      {data.map((item, idx) => {
        const heightPercent = (item.value / maxValue) * 100;
        return (
          <div key={idx} className="flex-1 flex flex-col items-center gap-2">
            <div className="w-full flex flex-col items-center justify-end" style={{ height: height - 40 }}>
              {showValues && item.value > 0 && (
                <span className="text-xs text-slate-400 mb-1">{item.value}</span>
              )}
              <div
                className="w-full rounded-t-md transition-all duration-500 ease-out"
                style={{
                  height: `${Math.max(heightPercent, 2)}%`,
                  background: item.color || 'linear-gradient(to top, #3b82f6, #06b6d4)',
                  minHeight: item.value > 0 ? '4px' : '0px'
                }}
              />
            </div>
            <span className="text-xs text-slate-500 truncate w-full text-center">
              {item.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}

interface ActivityHeatmapProps {
  data: { date: string; count: number }[];
  className?: string;
}

export function ActivityHeatmap({ data, className = '' }: ActivityHeatmapProps) {
  const maxCount = Math.max(...data.map(d => d.count), 1);

  const getIntensity = (count: number) => {
    if (count === 0) return 'bg-slate-800';
    const ratio = count / maxCount;
    if (ratio <= 0.25) return 'bg-blue-900/50';
    if (ratio <= 0.5) return 'bg-blue-700/60';
    if (ratio <= 0.75) return 'bg-blue-500/70';
    return 'bg-cyan-400/80';
  };

  // Group by weeks (7 days per row)
  const weeks = useMemo(() => {
    const result: typeof data[] = [];
    for (let i = 0; i < data.length; i += 7) {
      result.push(data.slice(i, i + 7));
    }
    return result;
  }, [data]);

  return (
    <div className={`space-y-1 ${className}`}>
      <div className="flex gap-1">
        {weeks.map((week, weekIdx) => (
          <div key={weekIdx} className="flex flex-col gap-1">
            {week.map((day, dayIdx) => (
              <div
                key={dayIdx}
                className={`w-3 h-3 rounded-sm ${getIntensity(day.count)} transition-colors`}
                title={`${day.date}: ${day.count} activities`}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="flex items-center gap-2 mt-3">
        <span className="text-xs text-slate-500">Less</span>
        <div className="flex gap-1">
          <div className="w-3 h-3 rounded-sm bg-slate-800" />
          <div className="w-3 h-3 rounded-sm bg-blue-900/50" />
          <div className="w-3 h-3 rounded-sm bg-blue-700/60" />
          <div className="w-3 h-3 rounded-sm bg-blue-500/70" />
          <div className="w-3 h-3 rounded-sm bg-cyan-400/80" />
        </div>
        <span className="text-xs text-slate-500">More</span>
      </div>
    </div>
  );
}

interface DonutChartProps {
  data: { label: string; value: number; color: string }[];
  size?: number;
  thickness?: number;
  className?: string;
}

export function DonutChart({
  data,
  size = 120,
  thickness = 20,
  className = ''
}: DonutChartProps) {
  const total = data.reduce((sum, d) => sum + d.value, 0);
  const radius = (size - thickness) / 2;
  const circumference = 2 * Math.PI * radius;

  let currentOffset = 0;

  const segments = data.map((item, idx) => {
    const percent = total > 0 ? item.value / total : 0;
    const strokeLength = circumference * percent;
    const offset = currentOffset;
    currentOffset += strokeLength;

    return {
      ...item,
      strokeDasharray: `${strokeLength} ${circumference}`,
      strokeDashoffset: -offset,
    };
  });

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={thickness}
          className="text-slate-800"
        />
        {/* Data segments */}
        {segments.map((segment, idx) => (
          <circle
            key={idx}
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={segment.color}
            strokeWidth={thickness}
            strokeDasharray={segment.strokeDasharray}
            strokeDashoffset={segment.strokeDashoffset}
            className="transition-all duration-500"
          />
        ))}
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-2xl font-bold text-white">{total}</span>
      </div>
    </div>
  );
}

interface TrendLineProps {
  data: number[];
  width?: number;
  height?: number;
  color?: string;
  className?: string;
}

export function TrendLine({
  data,
  width = 100,
  height = 40,
  color = '#3b82f6',
  className = ''
}: TrendLineProps) {
  if (data.length < 2) return null;

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;

  const points = data.map((value, idx) => {
    const x = (idx / (data.length - 1)) * width;
    const y = height - ((value - min) / range) * height;
    return `${x},${y}`;
  }).join(' ');

  const trend = data[data.length - 1] >= data[0] ? 'up' : 'down';
  const trendColor = trend === 'up' ? '#10b981' : '#ef4444';

  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      <svg width={width} height={height} className="overflow-visible">
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      <span
        className="text-xs font-medium"
        style={{ color: trendColor }}
      >
        {trend === 'up' ? '↑' : '↓'}
      </span>
    </div>
  );
}

interface LineChartProps {
  data: { label: string; value: number }[];
  width?: number;
  height?: number;
  color?: string;
  className?: string;
}

export function LineChart({
  data,
  width = 480,
  height = 140,
  color = '#3b82f6',
  className = '',
}: LineChartProps) {
  if (data.length < 2) {
    return (
      <div className={`flex items-center justify-center text-xs text-slate-500 ${className}`} style={{ height }}>
        Not enough history yet — check back after another period is scored.
      </div>
    );
  }

  const padTop = 12;
  const padBottom = 24;
  const plotHeight = height - padTop - padBottom;
  const max = Math.max(...data.map(d => d.value));
  const min = Math.min(...data.map(d => d.value));
  const range = max - min || 1;

  const points = data.map((d, idx) => {
    const x = (idx / (data.length - 1)) * width;
    const y = padTop + plotHeight - ((d.value - min) / range) * plotHeight;
    return { x, y, ...d };
  });

  const linePoints = points.map(p => `${p.x},${p.y}`).join(' ');
  const areaPoints = `0,${height - padBottom} ${linePoints} ${width},${height - padBottom}`;

  return (
    <div className={className}>
      <svg width="100%" height={height} viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none" className="overflow-visible">
        <polygon points={areaPoints} fill={color} opacity={0.08} />
        <polyline points={linePoints} fill="none" stroke={color} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
        {points.map((p, idx) => (
          <circle key={idx} cx={p.x} cy={p.y} r={3} fill={color}>
            <title>{`${p.label}: ${p.value.toFixed(1)}`}</title>
          </circle>
        ))}
      </svg>
      <div className="flex justify-between mt-1">
        {points.map((p, idx) => (
          <span key={idx} className="text-[10px] text-slate-500">
            {idx === 0 || idx === points.length - 1 || points.length <= 6 ? p.label : ''}
          </span>
        ))}
      </div>
    </div>
  );
}

interface ProgressRingProps {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  className?: string;
}

export function ProgressRing({
  value,
  max = 100,
  size = 80,
  strokeWidth = 8,
  className = ''
}: ProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const percent = Math.min(value / max, 1);
  const offset = circumference * (1 - percent);

  return (
    <div className={`relative inline-flex items-center justify-center ${className}`}>
      <svg width={size} height={size} className="transform -rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="currentColor"
          strokeWidth={strokeWidth}
          className="text-slate-700"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="url(#gradient)"
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-500"
        />
        <defs>
          <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#3b82f6" />
            <stop offset="100%" stopColor="#06b6d4" />
          </linearGradient>
        </defs>
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-lg font-bold text-white">{Math.round(percent * 100)}%</span>
      </div>
    </div>
  );
}
