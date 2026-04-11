import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

interface BodyMetricPoint {
  date: string;
  weight: number | null;
}

export default function BodyMetricsChart({
  data,
}: {
  data: BodyMetricPoint[];
}) {
  const rootStyle =
    typeof window !== 'undefined'
      ? getComputedStyle(document.documentElement)
      : null;
  const cssVar = (name: string, fallback: string) =>
    rootStyle?.getPropertyValue(name).trim() || fallback;
  const grid = cssVar('--border', '#e5e5e5');
  const axis = cssVar('--text-dim', '#555555');
  const tooltipBg = cssVar('--bg-card', '#f5f5f5');
  const tooltipText = cssVar('--text', '#333333');
  const line = cssVar('--tenant-primary', '#333333');

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} />
        <XAxis dataKey="date" stroke={axis} fontSize={11} />
        <YAxis stroke={axis} fontSize={11} domain={['auto', 'auto']} />
        <Tooltip
          contentStyle={{
            background: tooltipBg,
            border: `1px solid ${grid}`,
            borderRadius: 8,
            fontSize: 12,
            color: tooltipText,
          }}
          labelStyle={{ color: axis }}
        />
        <Line
          type="monotone"
          dataKey="weight"
          stroke={line}
          strokeWidth={2}
          dot={{ r: 3 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
