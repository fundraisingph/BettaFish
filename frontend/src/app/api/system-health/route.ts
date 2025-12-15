import { NextRequest, NextResponse } from 'next/server';

// Mock data for system health
const systemHealthData = {
  cpu: 45,
  memory: 62,
  storage: 38,
  network: 78,
  timestamp: new Date().toISOString()
};

export async function GET(request: NextRequest) {
  try {
    // Simulate real-time data changes
    const cpu = Math.min(100, Math.max(0, systemHealthData.cpu + (Math.random() - 0.5) * 10));
    const memory = Math.min(100, Math.max(0, systemHealthData.memory + (Math.random() - 0.5) * 8));
    const storage = Math.min(100, Math.max(0, systemHealthData.storage + (Math.random() - 0.5) * 5));
    const network = Math.min(100, Math.max(0, systemHealthData.network + (Math.random() - 0.5) * 15));

    const updatedData = {
      cpu: parseFloat(cpu.toFixed(1)),
      memory: parseFloat(memory.toFixed(1)),
      storage: parseFloat(storage.toFixed(1)),
      network: parseFloat(network.toFixed(1)),
      timestamp: new Date().toISOString()
    };

    // Update the stored values
    Object.assign(systemHealthData, updatedData);

    return NextResponse.json({
      success: true,
      data: updatedData
    });
  } catch (error) {
    console.error('Error fetching system health:', error);
    return NextResponse.json(
      { success: false, error: 'Failed to fetch system health data' },
      { status: 500 }
    );
  }
}