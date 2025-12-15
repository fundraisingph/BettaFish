"use client";

import { useState, useEffect, useCallback } from 'react';
import { enginesApi, EngineStatus, AnalysisResponse, ProgressUpdate } from '@/lib/api/engines';
import { useWebSocket } from '@/lib/websocket/client';
import { useAuth } from '@/contexts/auth-context';

export function useEngines() {
  const [engines, setEngines] = useState<EngineStatus[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [analyses, setAnalyses] = useState<AnalysisResponse[]>([]);
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResponse | null>(null);
  const [progress, setProgress] = useState<Record<string, ProgressUpdate>>({});
  
  const { isAuthenticated } = useAuth();
  const ws = useWebSocket();

  // Fetch engine statuses
  const fetchEngineStatuses = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      setIsLoading(true);
      const response = await enginesApi.getEngineStatuses();
      if (response.success && response.data) {
        setEngines(response.data);
        setError(null);
      } else {
        setError(response.error || 'Failed to fetch engine statuses');
      }
    } catch (err) {
      setError('Network error while fetching engine statuses');
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated]);

  // Fetch analysis history
  const fetchAnalysisHistory = useCallback(async () => {
    if (!isAuthenticated) return;
    
    try {
      const response = await enginesApi.getAnalysisHistory();
      if (response.success && response.data) {
        setAnalyses(response.data.analyses);
      }
    } catch (err) {
      console.error('Failed to fetch analysis history:', err);
    }
  }, [isAuthenticated]);

  // Start analysis
  const startAnalysis = useCallback(async (query: string, selectedEngines: string[]) => {
    if (!isAuthenticated) return { success: false, error: 'Not authenticated' };
    
    try {
      const response = await enginesApi.startAnalysis({
        query,
        engines: selectedEngines,
        options: {
          max_results: 100,
          sentiment_analysis: true,
          include_images: true,
        },
      });
      
      if (response.success && response.data) {
        setCurrentAnalysis(response.data);
        setAnalyses(prev => [response.data!, ...prev]);
        
        // Join WebSocket room for this analysis
        ws.joinAnalysisRoom(response.data.id);
        
        return { success: true, analysisId: response.data.id };
      } else {
        return { success: false, error: response.error || 'Failed to start analysis' };
      }
    } catch (err) {
      return { success: false, error: 'Network error while starting analysis' };
    }
  }, [isAuthenticated, ws]);

  // Stop analysis
  const stopAnalysis = useCallback(async (analysisId: string) => {
    if (!isAuthenticated) return { success: false, error: 'Not authenticated' };
    
    try {
      const response = await enginesApi.stopAnalysis(analysisId);
      if (response.success) {
        // Leave WebSocket room
        ws.leaveAnalysisRoom(analysisId);
        
        // Update current analysis if it's the one being stopped
        if (currentAnalysis?.id === analysisId) {
          setCurrentAnalysis(prev => prev ? { ...prev, status: 'failed' } : null);
        }
        
        return { success: true };
      } else {
        return { success: false, error: response.error || 'Failed to stop analysis' };
      }
    } catch (err) {
      return { success: false, error: 'Network error while stopping analysis' };
    }
  }, [isAuthenticated, currentAnalysis, ws]);

  // Restart engine
  const restartEngine = useCallback(async (engineId: string) => {
    if (!isAuthenticated) return { success: false, error: 'Not authenticated' };
    
    try {
      const response = await enginesApi.restartEngine(engineId);
      if (response.success) {
        // Refresh engine statuses
        fetchEngineStatuses();
        return { success: true };
      } else {
        return { success: false, error: response.error || 'Failed to restart engine' };
      }
    } catch (err) {
      return { success: false, error: 'Network error while restarting engine' };
    }
  }, [isAuthenticated, fetchEngineStatuses]);

  // Get analysis results
  const getAnalysisResults = useCallback(async (analysisId: string) => {
    if (!isAuthenticated) return null;
    
    try {
      const response = await enginesApi.getAnalysisResults(analysisId);
      if (response.success && response.data) {
        return response.data;
      }
      return null;
    } catch (err) {
      console.error('Failed to get analysis results:', err);
      return null;
    }
  }, [isAuthenticated]);

  // Initialize data and WebSocket connection
  useEffect(() => {
    if (isAuthenticated) {
      fetchEngineStatuses();
      fetchAnalysisHistory();
      
      // Connect to WebSocket
      const token = localStorage.getItem('access_token');
      ws.connect(token || undefined).then(() => {
        // Set up WebSocket event listeners
        ws.on('engine_progress', (data: ProgressUpdate) => {
          setProgress(prev => ({
            ...prev,
            [`${data.analysis_id}_${data.engine}`]: data,
          }));
        });
        
        ws.on('engine_status', (data: EngineStatus) => {
          setEngines(prev => 
            prev.map(engine => 
              engine.id === data.id ? data : engine
            )
          );
        });
        
        ws.on('analysis_complete', (data: AnalysisResponse) => {
          setCurrentAnalysis(data);
          setAnalyses(prev => 
            prev.map(analysis => 
              analysis.id === data.id ? data : analysis
            )
          );
          ws.leaveAnalysisRoom(data.id);
        });
        
        ws.on('notification', (data: any) => {
          // Handle notifications (could be displayed as toasts)
          console.log('Notification:', data);
        });
      }).catch(console.error);
    }
    
    return () => {
      ws.disconnect();
    };
  }, [isAuthenticated, fetchEngineStatuses, fetchAnalysisHistory, ws]);

  // Get progress for a specific analysis and engine
  const getProgress = useCallback((analysisId: string, engine: string) => {
    return progress[`${analysisId}_${engine}`] || null;
  }, [progress]);

  return {
    // Data
    engines,
    analyses,
    currentAnalysis,
    progress,
    isLoading,
    error,
    
    // Actions
    fetchEngineStatuses,
    fetchAnalysisHistory,
    startAnalysis,
    stopAnalysis,
    restartEngine,
    getAnalysisResults,
    getProgress,
    
    // Computed
    activeEngines: engines.filter(engine => engine.status === 'active'),
    idleEngines: engines.filter(engine => engine.status === 'idle'),
    maintenanceEngines: engines.filter(engine => engine.status === 'maintenance'),
    errorEngines: engines.filter(engine => engine.status === 'error'),
  };
}