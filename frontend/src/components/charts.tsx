"use client";

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, TooltipProps } from 'recharts';
import { LineChart as LineChartIcon, PieChart as PieChartIcon, BarChart3, TrendingUp } from 'lucide-react';

// Mock data for charts
const weeklyTrendData = [
  { name: 'Mon', performance: 65, queries: 1200 },
  { name: 'Tue', performance: 78, queries: 1900 },
  { name: 'Wed', performance: 82, queries: 2400 },
  { name: 'Thu', performance: 71, queries: 2100 },
  { name: 'Fri', performance: 89, queries: 3200 },
  { name: 'Sat', performance: 94, queries: 3800 },
  { name: 'Sun', performance: 87, queries: 2900 }
];

const engineUsageData = [
  { name: 'Data Engine', value: 35, color: '#3B82F6' },
  { name: 'Analytics Engine', value: 25, color: '#8B5CF6' },
  { name: 'Social Engine', value: 20, color: '#10B981' },
  { name: 'Content Engine', value: 15, color: '#F59E0B' },
  { name: 'Security Engine', value: 5, color: '#EF4444' }
];

const platformActivityData = [
  { platform: 'Twitter', activity: 4500, growth: 12 },
  { platform: 'Facebook', activity: 3200, growth: -5 },
  { platform: 'Instagram', activity: 5800, growth: 18 },
  { platform: 'LinkedIn', activity: 2100, growth: 8 },
  { platform: 'TikTok', activity: 6900, growth: 25 }
];

const heatmapData = Array.from({ length: 7 }, (_, i) => 
  Array.from({ length: 24 }, (_, j) => ({
    hour: j,
    day: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][i],
    value: Math.floor(Math.random() * 100)
  }))
).flat();

const CustomTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-black/80 backdrop-blur-xl border border-white/20 rounded-lg p-3 text-white">
        <p className="text-sm font-medium">{`${label}`}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm" style={{ color: entry.color }}>
            {`${entry.name}: ${entry.value}`}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export function WeeklyTrendChart() {
  return (
    <Card className="bg-black/20 backdrop-blur-xl border-white/10 text-white">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <LineChartIcon className="w-5 h-5 text-blue-400" />
          Weekly Trend Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={weeklyTrendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis 
                dataKey="name" 
                stroke="rgba(255,255,255,0.5)"
                tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 12 }}
              />
              <YAxis 
                stroke="rgba(255,255,255,0.5)"
                tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 12 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Line 
                type="monotone" 
                dataKey="performance" 
                stroke="#3B82F6" 
                strokeWidth={3}
                dot={{ fill: '#3B82F6', r: 4 }}
                activeDot={{ r: 6 }}
                name="Performance %"
              />
              <Line 
                type="monotone" 
                dataKey="queries" 
                stroke="#8B5CF6" 
                strokeWidth={3}
                dot={{ fill: '#8B5CF6', r: 4 }}
                activeDot={{ r: 6 }}
                name="Queries"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

export function EngineUsageChart() {
  return (
    <Card className="bg-black/20 backdrop-blur-xl border-white/10 text-white">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <PieChartIcon className="w-5 h-5 text-purple-400" />
          Engine Usage Distribution
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={engineUsageData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {engineUsageData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

export function PlatformActivityChart() {
  return (
    <Card className="bg-black/20 backdrop-blur-xl border-white/10 text-white">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <BarChart3 className="w-5 h-5 text-green-400" />
          Platform Activity
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={platformActivityData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis 
                dataKey="platform" 
                stroke="rgba(255,255,255,0.5)"
                tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 12 }}
              />
              <YAxis 
                stroke="rgba(255,255,255,0.5)"
                tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 12 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey="activity" 
                fill="#10B981"
                radius={[8, 8, 0, 0]}
                name="Activity"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}

export function ActivityHeatmap() {
  const getHeatmapColor = (value: number) => {
    if (value < 20) return 'bg-green-500/20';
    if (value < 40) return 'bg-green-500/40';
    if (value < 60) return 'bg-yellow-500/40';
    if (value < 80) return 'bg-orange-500/40';
    return 'bg-red-500/40';
  };

  const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  const hours = Array.from({ length: 24 }, (_, i) => i);

  return (
    <Card className="bg-black/20 backdrop-blur-xl border-white/10 text-white">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <TrendingUp className="w-5 h-5 text-orange-400" />
          Activity Heatmap (7 Days)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <div className="w-12"></div>
            <div className="flex-1 grid grid-cols-24 gap-1">
              {hours.map(hour => (
                <div key={hour} className="text-xs text-center text-gray-400">
                  {hour % 6 === 0 ? hour : ''}
                </div>
              ))}
            </div>
          </div>
          {days.map((day, dayIndex) => (
            <div key={day} className="flex items-center gap-2">
              <div className="w-12 text-sm text-gray-400">{day}</div>
              <div className="flex-1 grid grid-cols-24 gap-1">
                {hours.map(hour => {
                  const dataPoint = heatmapData.find(d => d.day === day && d.hour === hour);
                  return (
                    <div
                      key={hour}
                      className={`aspect-square rounded-sm ${getHeatmapColor(dataPoint?.value || 0)} border border-white/10 hover:border-white/30 transition-colors cursor-pointer`}
                      title={`${day} ${hour}:00 - ${dataPoint?.value || 0}% activity`}
                    />
                  );
                })}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 flex items-center justify-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-green-500/20 border border-white/20 rounded-sm"></div>
            <span className="text-gray-400">Low</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-yellow-500/40 border border-white/20 rounded-sm"></div>
            <span className="text-gray-400">Medium</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-orange-500/40 border border-white/20 rounded-sm"></div>
            <span className="text-gray-400">High</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-red-500/40 border border-white/20 rounded-sm"></div>
            <span className="text-gray-400">Very High</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}