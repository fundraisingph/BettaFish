import { NextRequest, NextResponse } from 'next/server';

// Mock activities data
const activitiesData = [
  { 
    id: 1, 
    type: 'analysis', 
    title: 'Completed social media analysis', 
    description: 'Analyzed 5,000+ social media posts for sentiment analysis',
    time: '2 minutes ago',
    timestamp: new Date(Date.now() - 2 * 60 * 1000).toISOString(),
    icon: 'bar-chart',
    severity: 'info'
  },
  { 
    id: 2, 
    type: 'alert', 
    title: 'High CPU usage detected', 
    description: 'CPU usage exceeded 80% threshold for more than 5 minutes',
    time: '5 minutes ago',
    timestamp: new Date(Date.now() - 5 * 60 * 1000).toISOString(),
    icon: 'alert',
    severity: 'warning'
  },
  { 
    id: 3, 
    type: 'engine', 
    title: 'Analytics Engine restarted', 
    description: 'Automatic restart due to memory optimization',
    time: '12 minutes ago',
    timestamp: new Date(Date.now() - 12 * 60 * 1000).toISOString(),
    icon: 'zap',
    severity: 'info'
  },
  { 
    id: 4, 
    type: 'data', 
    title: 'New data batch processed', 
    description: 'Processed 10,000 records from Twitter API',
    time: '18 minutes ago',
    timestamp: new Date(Date.now() - 18 * 60 * 1000).toISOString(),
    icon: 'database',
    severity: 'success'
  },
  { 
    id: 5, 
    type: 'user', 
    title: 'New user registration', 
    description: 'User john.doe@example.com joined the platform',
    time: '25 minutes ago',
    timestamp: new Date(Date.now() - 25 * 60 * 1000).toISOString(),
    icon: 'user',
    severity: 'info'
  },
  { 
    id: 6, 
    type: 'security', 
    title: 'Security scan completed', 
    description: 'Weekly security scan found no vulnerabilities',
    time: '1 hour ago',
    timestamp: new Date(Date.now() - 60 * 60 * 1000).toISOString(),
    icon: 'shield',
    severity: 'success'
  },
  { 
    id: 7, 
    type: 'performance', 
    title: 'Query optimization applied', 
    description: 'Database queries optimized for 25% performance improvement',
    time: '2 hours ago',
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    icon: 'trending-up',
    severity: 'success'
  },
  { 
    id: 8, 
    type: 'backup', 
    title: 'Automated backup completed', 
    description: 'Daily backup of all user data completed successfully',
    time: '3 hours ago',
    timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    icon: 'hard-drive',
    severity: 'info'
  }
];

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '10');
    const offset = parseInt(searchParams.get('offset') || '0');

    // Simulate real-time updates by occasionally adding new activities
    const shouldAddNew = Math.random() > 0.7;
    let updatedActivities = [...activitiesData];

    if (shouldAddNew) {
      const newActivity = {
        id: Date.now(),
        type: 'system',
        title: 'Real-time system update',
        description: 'System performance metrics updated',
        time: 'Just now',
        timestamp: new Date().toISOString(),
        icon: 'activity',
        severity: 'info'
      };
      updatedActivities.unshift(newActivity);
    }

    // Paginate results
    const paginatedActivities = updatedActivities.slice(offset, offset + limit);

    return NextResponse.json({
      success: true,
      data: paginatedActivities,
      total: updatedActivities.length,
      hasMore: offset + limit < updatedActivities.length
    });
  } catch (error) {
    console.error('Error fetching activities:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch activities' },
      { status: 500 }
    );
  }
}