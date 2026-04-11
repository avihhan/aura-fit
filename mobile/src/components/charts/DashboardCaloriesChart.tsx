import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from 'recharts';

interface CaloriesPoint {
  day: string;
  cal: number;
}

export default function DashboardCaloriesChart({
  data,
}: {
  data: CaloriesPoint[];
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
  const bar = cssVar('--tenant-primary', '#333333');

  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke={grid} />
        <XAxis dataKey="day" stroke={axis} fontSize={11} />
        <YAxis stroke={axis} fontSize={11} />
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
        <Bar dataKey="cal" fill={bar} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
