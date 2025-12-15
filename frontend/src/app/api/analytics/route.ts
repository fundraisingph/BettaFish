import { NextRequest, NextResponse } from 'next/server';

// Mock analytics data
const weeklyTrendData = [
  { name: 'Mon', performance: 65, queries: 1200, users: 450, revenue: 2400 },
  { name: 'Tue', performance: 78, queries: 1900, users: 620, revenue: 3100 },
  { name: 'Wed', performance: 82, queries: 2400, users: 780, revenue: 4200 },
  { name: 'Thu', performance: 71, queries: 2100, users: 690, revenue: 3800 },
  { name: 'Fri', performance: 89, queries: 3200, users: 920, revenue: 5600 },
  { name: 'Sat', performance: 94, queries: 3800, users: 1100, revenue: 6200 },
  { name: 'Sun', performance: 87, queries: 2900, users: 850, revenue: 4800 }
];

const engineUsageData = [
  { name: 'Data Engine', value: 35, color: '#3B82F6', queries: 15234 },
  { name: 'Analytics Engine', value: 25, color: '#8B5CF6', queries: 10892 },
  { name: 'Social Engine', value: 20, color: '#10B981', queries: 8567 },
  { name: 'Content Engine', value: 15, color: '#F59E0B', queries: 6234 },
  { name: 'Security Engine', value: 5, color: '#EF4444', queries: 2445 }
];

const platformActivityData = [
  { platform: 'Twitter', activity: 4500, growth: 12, users: 120000 },
  { platform: 'Facebook', activity: 3200, growth: -5, users: 98000 },
  { platform: 'Instagram', activity: 5800, growth: 18, users: 156000 },
  { platform: 'LinkedIn', activity: 2100, growth: 8, users: 67000 },
  { platform: 'TikTok', activity: 6900, growth: 25, users: 234000 }
];

const heatmapData = Array.from({ length: 7 }, (_, i) => 
  Array.from({ length: 24 }, (_, j) => ({
    hour: j,
    day: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][i],
    value: Math.floor(Math.random() * 100)
  }))
).flat();

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get('type');

    let data;

    switch (type) {
      case 'weekly-trend':
        // Simulate real-time data updates
        data = weeklyTrendData.map(item => ({
          ...item,
          performance: Math.min(100, Math.max(0, item.performance + (Math.random() - 0.5) * 10)),
          queries: Math.max(100, item.queries + Math.floor((Math.random() - 0.5) * 200)),
          users: Math.max(100, item.users + Math.floor((Math.random() - 0.5) * 100)),
          revenue: Math.max(100, item.revenue + Math.floor((Math.random() - 0.5) * 500))
        }));
        break;

      case 'engine-usage':
        // Simulate changing engine usage
        const total = 100;
        const newData = engineUsageData.map(engine => ({
          ...engine,
          value: Math.max(5, engine.value + (Math.random() - 0.5) * 5),
          queries: engine.queries + Math.floor(Math.random() * 50)
        }));
        
        // Normalize to ensure total is 100%
        const currentTotal = newData.reduce((sum, engine) => sum + engine.value, 0);
        data = newData.map(engine => ({
          ...engine,
          value: parseFloat(((engine.value / currentTotal) * total).toFixed(1))
        }));
        break;

      case 'platform-activity':
        // Simulate platform activity changes
        data = platformActivityData.map(platform => ({
          ...platform,
          activity: Math.max(100, platform.activity + Math.floor((Math.random() - 0.5) * 500)),
          growth: parseFloat((platform.growth + (Math.random() - 0.5) * 2).toFixed(1)),
          users: Math.max(10000, platform.users + Math.floor((Math.random() - 0.5) * 5000))
        }));
        break;

      case 'heatmap':
        // Generate new heatmap data
        data = Array.from({ length: 7 }, (_, i) => 
          Array.from({ length: 24 }, (_, j) => ({
            hour: j,
            day: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'][i],
            value: Math.floor(Math.random() * 100)
          }))
        ).flat();
        break;

      default:
        return NextResponse.json(
          { success: false, error: 'Invalid analytics type specified' },
          { status: 400 }
        );
    }

    return NextResponse.json({
      success: true,
      data: data,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('Error fetching analytics data:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch analytics data' },
      { status: 500 }
    );
  }
}