"use client";

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { WeeklyTrendChart, EngineUsageChart, PlatformActivityChart, ActivityHeatmap } from '@/components/charts';
import { useAuth } from '@/contexts/auth-context';
import { useEngines } from '@/hooks/use-engines';
import { useRouter } from 'next/navigation';
import { 
  Menu, 
  Search, 
  Play, 
  Pause, 
  Settings, 
  Activity, 
  Database, 
  Cpu, 
  HardDrive, 
  Wifi,
  TrendingUp,
  Users,
  MessageSquare,
  Share2,
  Heart,
  BarChart3,
  PieChart,
  LineChart,
  Calendar,
  Clock,
  Zap,
  Shield,
  Globe,
  Layers,
  Grid3x3,
  Bell,
  LogOut,
  ChevronRight,
  ChevronDown,
  Home,
  FileText,
  HelpCircle,
  User,
  TriangleAlert
} from 'lucide-react';

export default function BettaFishDashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [expandedSections, setExpandedSections] = useState({
    dashboard: true,
    analytics: false,
    engines: false,
    settings: false
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEngines, setSelectedEngines] = useState<string[]>(['insight', 'media', 'query']);

  const { user, logout, isAuthenticated } = useAuth();
  const {
    engines,
    isLoading,
    startAnalysis,
    stopAnalysis,
    restartEngine,
    currentAnalysis,
    getProgress,
    activeEngines,
    idleEngines,
    maintenanceEngines,
    errorEngines
  } = useEngines();
  
  const router = useRouter();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  if (!isAuthenticated) {
    return null;
  }

  // Mock system health data (would come from backend)
  const [systemHealth] = useState({
    cpu: 45,
    memory: 62,
    storage: 38,
    network: 78
  });

  // Mock activities (would come from backend)
  const [activities] = useState([
    { id: 1, type: 'analysis', title: 'Completed social media analysis', time: '2 minutes ago', icon: BarChart3 },
    { id: 2, type: 'alert', title: 'High CPU usage detected', time: '5 minutes ago', icon: TriangleAlert },
    { id: 3, type: 'engine', title: 'Analytics Engine restarted', time: '12 minutes ago', icon: Zap },
    { id: 4, type: 'data', title: 'New data batch processed', time: '18 minutes ago', icon: Database },
    { id: 5, type: 'user', title: 'New user registration', time: '25 minutes ago', icon: User }
  ]);

  // Remove the useEffect since we're using mock data for systemHealth
  // useEffect(() => {
  //   // Simulate real-time updates
  //   const interval = setInterval(() => {
  //     setSystemHealth(prev => ({
  //       cpu: Math.min(100, Math.max(0, prev.cpu + (Math.random() - 0.5) * 10)),
  //       memory: Math.min(100, Math.max(0, prev.memory + (Math.random() - 0.5) * 8)),
  //       storage: Math.min(100, Math.max(0, prev.storage + (Math.random() - 0.5) * 5)),
  //       network: Math.min(100, Math.max(0, prev.network + (Math.random() - 0.5) * 15))
  //     }));
  //   }, 3000);

  //   return () => clearInterval(interval);
  // }, []);

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section as keyof typeof prev]
    }));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-500';
      case 'idle': return 'bg-yellow-500';
      case 'maintenance': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active': return <Badge className="bg-green-500/20 text-green-400 border-green-500/30">Active</Badge>;
      case 'idle': return <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">Idle</Badge>;
      case 'maintenance': return <Badge className="bg-red-500/20 text-red-400 border-red-500/30">Maintenance</Badge>;
      default: return <Badge className="bg-gray-500/20 text-gray-400 border-gray-500/30">Unknown</Badge>;
    }
  };

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-black/20 backdrop-blur-xl border-r border-white/10">
      {/* Logo Section */}
      <div className="p-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-white">BettaFish</h1>
            <p className="text-xs text-gray-400">Analytics Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 p-4 space-y-2">
        {/* Dashboard Section */}
        <div>
          <button
            onClick={() => toggleSection('dashboard')}
            className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-white/10 transition-all duration-200 text-white"
          >
            <div className="flex items-center gap-3">
              <Home className="w-5 h-5" />
              <span className="font-medium">Dashboard</span>
            </div>
            {expandedSections.dashboard ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </button>
          {expandedSections.dashboard && (
            <div className="ml-8 mt-2 space-y-1">
              <button className="w-full text-left p-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded transition-all">
                Overview
              </button>
              <button className="w-full text-left p-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded transition-all">
                Analytics
              </button>
              <button className="w-full text-left p-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded transition-all">
                Reports
              </button>
            </div>
          )}
        </div>

        {/* Analytics Section */}
        <div>
          <button
            onClick={() => toggleSection('analytics')}
            className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-white/10 transition-all duration-200 text-white"
          >
            <div className="flex items-center gap-3">
              <BarChart3 className="w-5 h-5" />
              <span className="font-medium">Analytics</span>
            </div>
            {expandedSections.analytics ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </button>
          {expandedSections.analytics && (
            <div className="ml-8 mt-2 space-y-1">
              <button className="w-full text-left p-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded transition-all">
                Social Media
              </button>
              <button className="w-full text-left p-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded transition-all">
                Web Traffic
              </button>
              <button className="w-full text-left p-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded transition-all">
                User Behavior
              </button>
            </div>
          )}
        </div>

        {/* Engines Section */}
        <div>
          <button
            onClick={() => toggleSection('engines')}
            className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-white/10 transition-all duration-200 text-white"
          >
            <div className="flex items-center gap-3">
              <Cpu className="w-5 h-5" />
              <span className="font-medium">Engines</span>
            </div>
            {expandedSections.engines ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
          </button>
          {expandedSections.engines && (
            <div className="ml-8 mt-2 space-y-1">
              <button className="w-full text-left p-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded transition-all">
                Data Engine
              </button>
              <button className="w-full text-left p-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded transition-all">
                Analytics Engine
              </button>
              <button className="w-full text-left p-2 text-sm text-gray-400 hover:text-white hover:bg-white/5 rounded transition-all">
                Social Engine
              </button>
            </div>
          )}
        </div>

        {/* Other Menu Items */}
        <button className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-white/10 transition-all duration-200 text-white">
          <FileText className="w-5 h-5" />
          <span className="font-medium">Reports</span>
        </button>

        <button className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-white/10 transition-all duration-200 text-white">
          <Users className="w-5 h-5" />
          <span className="font-medium">Team</span>
        </button>

        <button className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-white/10 transition-all duration-200 text-white">
          <Settings className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </button>

        <button className="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-white/10 transition-all duration-200 text-white">
          <HelpCircle className="w-5 h-5" />
          <span className="font-medium">Help</span>
        </button>
      </nav>

      {/* User Profile Section */}
      <div className="p-4 border-t border-white/10">
        <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-white/10 transition-all duration-200">
          <Avatar className="w-10 h-10">
            <AvatarImage src="/api/placeholder/40/40" alt="User" />
            <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white">
              {user?.name?.charAt(0).toUpperCase() || 'U'}
            </AvatarFallback>
          </Avatar>
          <div className="flex-1">
            <p className="text-sm font-medium text-white">{user?.name || 'User'}</p>
            <p className="text-xs text-gray-400">{user?.email || 'user@example.com'}</p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="text-gray-400 hover:text-white"
            onClick={logout}
          >
            <LogOut className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900">
      {/* Desktop Sidebar */}
      <div className="hidden lg:block fixed left-0 top-0 h-full w-64 z-50">
        <SidebarContent />
      </div>

      {/* Mobile Sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetTrigger asChild>
          <Button
            variant="ghost"
            size="sm"
            className="lg:hidden fixed top-4 left-4 z-50 text-white hover:bg-white/10"
          >
            <Menu className="w-5 h-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="p-0 w-64 bg-black/20 backdrop-blur-xl border-white/10">
          <SidebarContent />
        </SheetContent>
      </Sheet>

      {/* Main Content */}
      <div className="lg:ml-64 p-4 lg:p-8">
        {/* Hero Section */}
        <div className="mb-8">
          <Card className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 backdrop-blur-xl border-white/10 text-white overflow-hidden relative">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10"></div>
            <CardHeader className="relative z-10">
              <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
                <div>
                  <CardTitle className="text-3xl font-bold mb-2">BettaFish Analytics Dashboard</CardTitle>
                  <p className="text-gray-300">Real-time monitoring and analysis platform</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="hidden lg:flex items-center gap-6 text-sm">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-400">1,234</p>
                      <p className="text-gray-400">Active Analyses</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-purple-400">45.2K</p>
                      <p className="text-gray-400">Data Points</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-400">12</p>
                      <p className="text-gray-400">Platforms</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent className="relative z-10">
              <div className="flex flex-col lg:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <Input
                    placeholder="Search analytics, reports, or settings..."
                    className="pl-10 bg-white/10 border-white/20 text-white placeholder-gray-400 focus:bg-white/15"
                  />
                </div>
                <Button
                  onClick={async () => {
                    if (currentAnalysis) {
                      await stopAnalysis(currentAnalysis.id);
                    } else if (searchQuery.trim()) {
                      await startAnalysis(searchQuery, selectedEngines);
                    }
                  }}
                  disabled={!searchQuery.trim() || isLoading}
                  className={`px-6 py-2 rounded-lg font-medium transition-all duration-300 ${
                    currentAnalysis
                      ? 'bg-red-600 hover:bg-red-700'
                      : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
                  } text-white border-0`}
                >
                  {currentAnalysis ? (
                    <>
                      <Pause className="w-4 h-4 mr-2" />
                      Stop Analysis
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Start Analysis
                    </>
                  )}
                </Button>
              </div>
              {currentAnalysis && (
                <div className="mt-4">
                  <div className="flex items-center gap-2 text-sm text-gray-300">
                    <Activity className="w-4 h-4 animate-pulse" />
                    <span>
                      Analysis in progress... {currentAnalysis.status}
                      {selectedEngines.map(engine => {
                        const progress = getProgress(currentAnalysis.id, engine);
                        return progress ? ` (${engine}: ${progress.progress}%)` : '';
                      }).join('')}
                    </span>
                  </div>
                  <div className="mt-2 space-y-1">
                    {selectedEngines.map(engine => {
                      const progress = getProgress(currentAnalysis.id, engine);
                      return progress ? (
                        <div key={engine} className="flex items-center gap-2">
                          <span className="text-xs text-gray-400 w-20">{engine}:</span>
                          <Progress value={progress.progress} className="flex-1 h-2 bg-white/20" />
                        </div>
                      ) : null;
                    })}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
          {/* System Health Monitoring */}
          <Card className="bg-black/20 backdrop-blur-xl border-white/10 text-white col-span-1 xl:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5 text-green-400" />
                System Health Monitoring
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">CPU</span>
                    <span className="text-sm font-medium">{systemHealth.cpu.toFixed(1)}%</span>
                  </div>
                  <Progress value={systemHealth.cpu} className="h-2 bg-white/20" />
                  <div className="flex items-center gap-1">
                    <Cpu className="w-3 h-3 text-blue-400" />
                    <span className="text-xs text-gray-400">Intel i9-12900K</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Memory</span>
                    <span className="text-sm font-medium">{systemHealth.memory.toFixed(1)}%</span>
                  </div>
                  <Progress value={systemHealth.memory} className="h-2 bg-white/20" />
                  <div className="flex items-center gap-1">
                    <Database className="w-3 h-3 text-purple-400" />
                    <span className="text-xs text-gray-400">32GB DDR5</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Storage</span>
                    <span className="text-sm font-medium">{systemHealth.storage.toFixed(1)}%</span>
                  </div>
                  <Progress value={systemHealth.storage} className="h-2 bg-white/20" />
                  <div className="flex items-center gap-1">
                    <HardDrive className="w-3 h-3 text-green-400" />
                    <span className="text-xs text-gray-400">2TB NVMe</span>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Network</span>
                    <span className="text-sm font-medium">{systemHealth.network.toFixed(1)}%</span>
                  </div>
                  <Progress value={systemHealth.network} className="h-2 bg-white/20" />
                  <div className="flex items-center gap-1">
                    <Wifi className="w-3 h-3 text-yellow-400" />
                    <span className="text-xs text-gray-400">10 Gbps</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions Panel */}
          <Card className="bg-black/20 backdrop-blur-xl border-white/10 text-white">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5 text-yellow-400" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                <Button variant="outline" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                  <BarChart3 className="w-4 h-4 mr-2" />
                  Reports
                </Button>
                <Button variant="outline" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                  <Users className="w-4 h-4 mr-2" />
                  Team
                </Button>
                <Button variant="outline" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                  <Settings className="w-4 h-4 mr-2" />
                  Settings
                </Button>
                <Button variant="outline" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                  <Bell className="w-4 h-4 mr-2" />
                  Alerts
                </Button>
                <Button variant="outline" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                  <Share2 className="w-4 h-4 mr-2" />
                  Export
                </Button>
                <Button variant="outline" className="bg-white/10 border-white/20 text-white hover:bg-white/20">
                  <Shield className="w-4 h-4 mr-2" />
                  Security
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Engine Status Dashboard */}
        <Card className="bg-black/20 backdrop-blur-xl border-white/10 text-white mb-8">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Cpu className="w-5 h-5 text-blue-400" />
              Engine Status Dashboard
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
              {engines.map((engine, index) => (
                <div
                  key={engine.id}
                  className="relative bg-white/5 rounded-lg p-4 border border-white/10 hover:bg-white/10 transition-all duration-300 hover:scale-105"
                >
                  <div className="absolute top-2 right-2">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(engine.status)} animate-pulse`}></div>
                  </div>
                  <h3 className="font-medium text-sm mb-2 pr-6">{engine.name}</h3>
                  {getStatusBadge(engine.status)}
                  <div className="mt-3 space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Queries:</span>
                      <span className="text-white">{engine.queries.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Latency:</span>
                      <span className="text-white">{engine.latency}ms</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Success:</span>
                      <span className="text-green-400">{engine.success_rate}%</span>
                    </div>
                    <div className="mt-2 pt-2 border-t border-white/10">
                      <Button
                        size="sm"
                        variant="outline"
                        className="w-full bg-white/10 border-white/20 text-white hover:bg-white/20"
                        onClick={() => restartEngine(engine.id)}
                        disabled={isLoading}
                      >
                        Restart
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Activity Feed and Data Visualization */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Activity Feed */}
          <Card className="bg-black/20 backdrop-blur-xl border-white/10 text-white lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="w-5 h-5 text-purple-400" />
                Activity Feed
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4 max-h-96 overflow-y-auto">
                {activities.map((activity) => {
                  const Icon = activity.icon;
                  return (
                    <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-all duration-200">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                        <Icon className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">{activity.title}</p>
                        <p className="text-xs text-gray-400">{activity.time}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Data Visualization */}
          <div className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <WeeklyTrendChart />
              <EngineUsageChart />
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <PlatformActivityChart />
              <ActivityHeatmap />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}