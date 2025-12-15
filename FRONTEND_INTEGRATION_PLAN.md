# Frontend Integration Plan for BettaFish

## Overview

This document outlines the integration strategy for the Next.js frontend with the new FastAPI backend. The plan focuses on maintaining a smooth user experience while transitioning from the Flask backend to FastAPI.

## Current Frontend Architecture

### Technology Stack
- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Custom component library
- **Database**: Prisma with SQLite (development) / PostgreSQL (production)
- **Real-time**: Socket.IO client for Flask communication

### Current Structure
```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── api/                # API routes
│   │   ├── globals.css         # Global styles
│   │   ├── layout.tsx          # Root layout
│   │   └── page.tsx            # Home page
│   ├── components/             # React components
│   │   └── ui/                 # UI component library
│   ├── hooks/                  # Custom React hooks
│   ├── lib/                    # Utility functions
│   └── types/                  # TypeScript type definitions
├── prisma/                     # Prisma schema and migrations
└── public/                     # Static assets
```

## Integration Strategy

### Phase 1: API Client Migration

#### 1.1 Create API Client Service
```typescript
// frontend/src/lib/api-client.ts
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { getAuthToken } from './auth'

export interface ApiError {
  message: string
  code?: string
  details?: any
}

export interface ApiResponse<T = any> {
  data: T
  message?: string
  success: boolean
}

class ApiClient {
  private client: AxiosInstance
  
  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    // Request interceptor for authentication
    this.client.interceptors.request.use(
      (config) => {
        const token = getAuthToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )
    
    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized access
          window.location.href = '/login'
        }
        return Promise.reject(error)
      }
    )
  }
  
  // Generic request method
  async request<T = any>(config: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response: AxiosResponse<ApiResponse<T>> = await this.client.request(config)
      return response.data
    } catch (error: any) {
      throw this.handleError(error)
    }
  }
  
  // HTTP methods
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'GET', url })
  }
  
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'POST', url, data })
  }
  
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'PUT', url, data })
  }
  
  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'PATCH', url, data })
  }
  
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    return this.request<T>({ ...config, method: 'DELETE', url })
  }
  
  private handleError(error: any): ApiError {
    if (error.response) {
      // Server responded with error status
      return {
        message: error.response.data.message || 'Server error',
        code: error.response.data.code,
        details: error.response.data.details,
      }
    } else if (error.request) {
      // Request was made but no response received
      return {
        message: 'Network error - no response from server',
        code: 'NETWORK_ERROR',
      }
    } else {
      // Something else happened
      return {
        message: error.message || 'Unknown error occurred',
        code: 'UNKNOWN_ERROR',
      }
    }
  }
}

export const apiClient = new ApiClient()
```

#### 1.2 Create API Service Modules
```typescript
// frontend/src/lib/api/engines.ts
import { apiClient } from '../api-client'
import { InsightRequest, InsightResponse, MediaRequest, MediaResponse } from '@/types'

export const enginesApi = {
  // Insight Engine
  async startInsightAnalysis(request: InsightRequest): Promise<InsightResponse> {
    return apiClient.post('/engines/insight/analyze', request)
  },
  
  async getInsightStatus(taskId: string): Promise<any> {
    return apiClient.get(`/engines/insight/status/${taskId}`)
  },
  
  async getInsightResults(taskId: string): Promise<any> {
    return apiClient.get(`/engines/insight/results/${taskId}`)
  },
  
  // Media Engine
  async startMediaAnalysis(request: MediaRequest): Promise<MediaResponse> {
    return apiClient.post('/engines/media/analyze', request)
  },
  
  async getMediaStatus(taskId: string): Promise<any> {
    return apiClient.get(`/engines/media/status/${taskId}`)
  },
  
  async getMediaResults(taskId: string): Promise<any> {
    return apiClient.get(`/engines/media/results/${taskId}`)
  },
  
  // Query Engine
  async startQueryAnalysis(request: any): Promise<any> {
    return apiClient.post('/engines/query/analyze', request)
  },
  
  async getQueryStatus(taskId: string): Promise<any> {
    return apiClient.get(`/engines/query/status/${taskId}`)
  },
  
  async getQueryResults(taskId: string): Promise<any> {
    return apiClient.get(`/engines/query/results/${taskId}`)
  },
  
  // Report Engine
  async generateReport(taskIds: string[]): Promise<any> {
    return apiClient.post('/engines/report/generate', { taskIds })
  },
  
  async getReportStatus(reportId: string): Promise<any> {
    return apiClient.get(`/engines/report/status/${reportId}`)
  },
  
  async getReport(reportId: string): Promise<any> {
    return apiClient.get(`/engines/report/${reportId}`)
  },
  
  async downloadReport(reportId: string, format: 'html' | 'pdf'): Promise<Blob> {
    const response = await apiClient.get(`/engines/report/${reportId}/download?format=${format}`, {
      responseType: 'blob',
    })
    return response.data
  },
}
```

### Phase 2: WebSocket Integration

#### 2.1 WebSocket Client Service
```typescript
// frontend/src/lib/websocket-client.ts
import { useEffect, useRef, useState, useCallback } from 'react'

export interface WebSocketMessage {
  type: string
  data: any
  timestamp?: string
}

export interface WebSocketStatus {
  connected: boolean
  connecting: boolean
  error?: string
}

export class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private messageHandlers: Map<string, (data: any) => void> = new Map()
  private statusHandlers: ((status: WebSocketStatus) => void)[] = []
  
  constructor(url: string) {
    this.url = url
  }
  
  connect(token?: string) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return
    }
    
    // Add token to URL if provided
    const wsUrl = token ? `${this.url}?token=${token}` : this.url
    
    this.ws = new WebSocket(wsUrl)
    this.updateStatus({ connected: false, connecting: true })
    
    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.updateStatus({ connected: true, connecting: false })
    }
    
    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data)
        this.handleMessage(message)
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error)
      }
    }
    
    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      this.updateStatus({ connected: false, connecting: false })
      this.scheduleReconnect()
    }
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      this.updateStatus({ connected: false, connecting: false, error: 'Connection error' })
    }
  }
  
  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.updateStatus({ connected: false, connecting: false })
  }
  
  private scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++
        this.connect()
      }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1))
    }
  }
  
  private handleMessage(message: WebSocketMessage) {
    const handler = this.messageHandlers.get(message.type)
    if (handler) {
      handler(message.data)
    }
  }
  
  private updateStatus(status: WebSocketStatus) {
    this.statusHandlers.forEach(handler => handler(status))
  }
  
  // Public API
  onMessage(type: string, handler: (data: any) => void) {
    this.messageHandlers.set(type, handler)
  }
  
  offMessage(type: string) {
    this.messageHandlers.delete(type)
  }
  
  onStatusChange(handler: (status: WebSocketStatus) => void) {
    this.statusHandlers.push(handler)
    return () => {
      const index = this.statusHandlers.indexOf(handler)
      if (index > -1) {
        this.statusHandlers.splice(index, 1)
      }
    }
  }
  
  sendMessage(message: WebSocketMessage) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        ...message,
        timestamp: new Date().toISOString(),
      }))
    } else {
      console.warn('WebSocket not connected, message not sent:', message)
    }
  }
}

// React Hook
export function useWebSocket(url: string, token?: string) {
  const client = useRef<WebSocketClient | null>(null)
  const [status, setStatus] = useState<WebSocketStatus>({
    connected: false,
    connecting: false,
  })
  
  useEffect(() => {
    client.current = new WebSocketClient(url)
    client.current.connect(token)
    
    const unsubscribe = client.current.onStatusChange(setStatus)
    
    return () => {
      unsubscribe()
      client.current?.disconnect()
    }
  }, [url, token])
  
  const onMessage = useCallback((type: string, handler: (data: any) => void) => {
    client.current?.onMessage(type, handler)
    return () => client.current?.offMessage(type)
  }, [])
  
  const sendMessage = useCallback((message: WebSocketMessage) => {
    client.current?.sendMessage(message)
  }, [])
  
  return { status, onMessage, sendMessage }
}
```

#### 2.2 Real-time Hooks
```typescript
// frontend/src/hooks/use-real-time-analysis.ts
import { useEffect, useState } from 'react'
import { useWebSocket } from '@/lib/websocket-client'
import { enginesApi } from '@/lib/api/engines'

export interface AnalysisTask {
  id: string
  type: 'insight' | 'media' | 'query'
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  logs: string[]
  result?: any
  error?: string
}

export function useRealTimeAnalysis() {
  const [tasks, setTasks] = useState<Map<string, AnalysisTask>>(new Map())
  const { status, onMessage } = useWebSocket(
    process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/frontend'
  )
  
  useEffect(() => {
    // Handle agent log messages
    const unsubscribeLogs = onMessage('agent_log', (data) => {
      setTasks(prev => {
        const newTasks = new Map(prev)
        const task = newTasks.get(data.taskId)
        
        if (task) {
          newTasks.set(data.taskId, {
            ...task,
            logs: [...task.logs, `[${data.timestamp}] ${data.level.toUpperCase()}: ${data.message}`],
            progress: task.progress + 5, // Estimate progress
          })
        }
        
        return newTasks
      })
    })
    
    // Handle system messages
    const unsubscribeSystem = onMessage('system', (data) => {
      if (data.action === 'agent_connected' || data.action === 'agent_disconnected') {
        // Update agent status
        console.log('Agent status changed:', data)
      }
    })
    
    // Handle forum messages
    const unsubscribeForum = onMessage('forum_message', (data) => {
      // Handle forum discussion messages
      console.log('Forum message:', data)
    })
    
    return () => {
      unsubscribeLogs()
      unsubscribeSystem()
      unsubscribeForum()
    }
  }, [onMessage])
  
  const startAnalysis = async (type: 'insight' | 'media' | 'query', query: string) => {
    try {
      let response
      
      switch (type) {
        case 'insight':
          response = await enginesApi.startInsightAnalysis({ query })
          break
        case 'media':
          response = await enginesApi.startMediaAnalysis({ query })
          break
        case 'query':
          response = await enginesApi.startQueryAnalysis({ query })
          break
      }
      
      // Add task to state
      setTasks(prev => {
        const newTasks = new Map(prev)
        newTasks.set(response.taskId, {
          id: response.taskId,
          type,
          status: 'running',
          progress: 0,
          logs: [`[${new Date().toISOString()}] Started ${type} analysis`],
        })
        return newTasks
      })
      
      return response.taskId
    } catch (error) {
      console.error(`Failed to start ${type} analysis:`, error)
      throw error
    }
  }
  
  const getTask = (taskId: string) => {
    return tasks.get(taskId)
  }
  
  const getAllTasks = () => {
    return Array.from(tasks.values())
  }
  
  return {
    tasks,
    connectionStatus: status,
    startAnalysis,
    getTask,
    getAllTasks,
  }
}
```

### Phase 3: Component Updates

#### 3.1 Analysis Dashboard Component
```typescript
// frontend/src/components/analysis-dashboard.tsx
'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useRealTimeAnalysis } from '@/hooks/use-real-time-analysis'
import { AnalysisTask } from '@/hooks/use-real-time-analysis'

export function AnalysisDashboard() {
  const [query, setQuery] = useState('')
  const { tasks, connectionStatus, startAnalysis, getAllTasks } = useRealTimeAnalysis()
  
  const handleStartAnalysis = async (type: 'insight' | 'media' | 'query') => {
    if (!query.trim()) return
    
    try {
      await startAnalysis(type, query)
    } catch (error) {
      console.error('Analysis failed:', error)
    }
  }
  
  const renderTaskCard = (task: AnalysisTask) => (
    <Card key={task.id} className="mb-4">
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="text-lg">{task.type.toUpperCase()} Analysis</CardTitle>
          <Badge variant={task.status === 'completed' ? 'default' : 
                         task.status === 'failed' ? 'destructive' : 
                         task.status === 'running' ? 'secondary' : 'outline'}>
            {task.status}
          </Badge>
        </div>
        <CardDescription>Task ID: {task.id}</CardDescription>
      </CardHeader>
      <CardContent>
        <Progress value={task.progress} className="mb-4" />
        
        <div className="space-y-2">
          <h4 className="font-medium">Logs:</h4>
          <div className="bg-gray-50 p-2 rounded h-32 overflow-y-auto text-sm font-mono">
            {task.logs.map((log, index) => (
              <div key={index}>{log}</div>
            ))}
          </div>
        </div>
        
        {task.error && (
          <div className="mt-4 p-2 bg-red-50 border border-red-200 rounded text-red-700">
            Error: {task.error}
          </div>
        )}
      </CardContent>
    </Card>
  )
  
  return (
    <div className="container mx-auto p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold mb-2">BettaFish Analysis Dashboard</h1>
        <p className="text-gray-600">
          Connection Status: {connectionStatus.connected ? 'Connected' : 'Disconnected'}
        </p>
      </div>
      
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>Start New Analysis</CardTitle>
          <CardDescription>Enter your query and select analysis type</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 mb-4">
            <Input
              placeholder="Enter your analysis query..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1"
            />
          </div>
          
          <Tabs defaultValue="insight" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="insight">Insight</TabsTrigger>
              <TabsTrigger value="media">Media</TabsTrigger>
              <TabsTrigger value="query">Query</TabsTrigger>
            </TabsList>
            
            <TabsContent value="insight" className="mt-4">
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  Database mining and sentiment analysis
                </p>
                <Button 
                  onClick={() => handleStartAnalysis('insight')}
                  disabled={!query.trim()}
                >
                  Start Insight Analysis
                </Button>
              </div>
            </TabsContent>
            
            <TabsContent value="media" className="mt-4">
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  Multimodal content analysis with web search
                </p>
                <Button 
                  onClick={() => handleStartAnalysis('media')}
                  disabled={!query.trim()}
                >
                  Start Media Analysis
                </Button>
              </div>
            </TabsContent>
            
            <TabsContent value="query" className="mt-4">
              <div className="space-y-2">
                <p className="text-sm text-gray-600">
                  Precise information search and query optimization
                </p>
                <Button 
                  onClick={() => handleStartAnalysis('query')}
                  disabled={!query.trim()}
                >
                  Start Query Analysis
                </Button>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
      
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Active Analyses</h2>
        {getAllTasks().length === 0 ? (
          <Card>
            <CardContent className="pt-6">
              <p className="text-center text-gray-500">No active analyses</p>
            </CardContent>
          </Card>
        ) : (
          getAllTasks().map(renderTaskCard)
        )}
      </div>
    </div>
  )
}
```

### Phase 4: Authentication Integration

#### 4.1 Authentication Context
```typescript
// frontend/src/contexts/auth-context.tsx
'use client'

import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { apiClient } from '@/lib/api-client'

interface User {
  id: string
  email: string
  name: string
  role: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  register: (email: string, password: string, name: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    checkAuth()
  }, [])
  
  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      if (token) {
        const response = await apiClient.get('/auth/me')
        setUser(response.data)
      }
    } catch (error) {
      localStorage.removeItem('auth_token')
    } finally {
      setLoading(false)
    }
  }
  
  const login = async (email: string, password: string) => {
    const response = await apiClient.post('/auth/login', { email, password })
    const { token, user: userData } = response.data
    
    localStorage.setItem('auth_token', token)
    setUser(userData)
  }
  
  const logout = async () => {
    try {
      await apiClient.post('/auth/logout')
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem('auth_token')
      setUser(null)
    }
  }
  
  const register = async (email: string, password: string, name: string) => {
    const response = await apiClient.post('/auth/register', { email, password, name })
    const { token, user: userData } = response.data
    
    localStorage.setItem('auth_token', token)
    setUser(userData)
  }
  
  return (
    <AuthContext.Provider value={{ user, loading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
```

### Phase 5: Migration Strategy

#### 5.1 Gradual Migration Approach
1. **Parallel Operation**: Run both Flask and FastAPI backends
2. **Feature Flags**: Use feature flags to switch between backends
3. **A/B Testing**: Test new backend with subset of users
4. **Gradual Rollout**: Increase usage of FastAPI backend over time

#### 5.2 Environment Configuration
```typescript
// frontend/src/lib/config.ts
export const config = {
  apiBaseUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  wsUrl: process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/frontend',
  useFastAPI: process.env.NEXT_PUBLIC_USE_FASTAPI === 'true',
  enableRealTime: process.env.NEXT_PUBLIC_ENABLE_REAL_TIME !== 'false',
}
```

#### 5.3 Compatibility Layer
```typescript
// frontend/src/lib/api-compatibility.ts
import { enginesApi } from './api/engines'
import { config } from './config'

// Legacy Flask API compatibility
class LegacyApiService {
  async startInsightAnalysis(query: string) {
    // Call Flask API
    const response = await fetch('/api/insight/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    })
    return response.json()
  }
  
  // Add other legacy methods...
}

export const apiService = config.useFastAPI ? enginesApi : new LegacyApiService()
```

## Testing Strategy

### Unit Testing
- Test API client methods
- Test WebSocket client functionality
- Test React hooks and components

### Integration Testing
- Test API integration with FastAPI backend
- Test WebSocket communication
- Test authentication flow

### End-to-End Testing
- Test complete user workflows
- Test real-time updates
- Test error handling

## Performance Considerations

### API Optimization
- Implement request caching
- Use React Query for data fetching
- Optimize bundle size

### WebSocket Optimization
- Implement connection pooling
- Use message batching
- Handle connection failures gracefully

### UI Optimization
- Implement virtual scrolling for large lists
- Use React.memo for component optimization
- Implement lazy loading

This integration plan ensures a smooth transition from Flask to FastAPI while maintaining a great user experience and leveraging the new backend's capabilities.