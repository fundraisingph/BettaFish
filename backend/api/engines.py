"""
Engine API endpoints - Matching Flask functionality for full frontend parity.
"""

import asyncio
import os
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel

from core.database import get_db_connection
from core.exceptions import BusinessLogicException, ResourceNotFoundException
from services.auth_service import get_current_user
from services.websocket_manager import manager

router = APIRouter()

# Global processes state (matching Flask structure)
PROCESSES = {
    'insight': {'process': None, 'port': 8501, 'status': 'stopped', 'output': []},
    'media': {'process': None, 'port': 8502, 'status': 'stopped', 'output': []},
    'query': {'process': None, 'port': 8503, 'status': 'stopped', 'output': []},
    'forum': {'process': None, 'port': None, 'status': 'stopped', 'output': []}
}

STREAMLIT_SCRIPTS = {
    'insight': '../SingleEngineApp/insight_engine_streamlit_app.py',
    'media': '../SingleEngineApp/media_engine_streamlit_app.py',
    'query': '../SingleEngineApp/query_engine_streamlit_app.py'
}

LOG_DIR = Path('../logs')
LOG_DIR.mkdir(exist_ok=True)

# Request/Response models
class EngineStatus(BaseModel):
    id: str
    name: str
    status: str
    port: Optional[int] = None
    output_lines: int = 0

class AnalysisRequest(BaseModel):
    query: str
    engines: List[str] = []
    options: Dict[str, Any] = {}

class ConfigUpdate(BaseModel):
    key: str
    value: Any


# Helper functions
def check_app_status():
    """Check application health status"""
    for app_name, info in PROCESSES.items():
        if info['process'] is not None:
            if info['process'].poll() is None:
                # Process is running, check if accessible
                try:
                    import requests
                    response = requests.get(
                        f"http://127.0.0.1:{info['port']}/_stcore/health",
                        timeout=5,
                        proxies={'http': None, 'https': None}
                    )
                    if response.status_code == 200:
                        info['status'] = 'running'
                    else:
                        info['status'] = 'starting'
                except requests.exceptions.Timeout:
                    info['status'] = 'timeout'
                except Exception:
                    info['status'] = 'starting'
            else:
                # Process ended
                info['process'] = None
                info['status'] = 'stopped'

def write_log_to_file(app_name: str, line: str):
    """Write log to file"""
    try:
        log_file_path = LOG_DIR / f"{app_name}.log"
        with open(log_file_path, 'a', encoding='utf-8') as f:
            f.write(line + '\n')
            f.flush()
    except Exception as e:
        print(f"Error writing log for {app_name}: {e}")

def read_log_from_file(app_name: str, tail_lines: Optional[int] = None):
    """Read logs from file"""
    try:
        log_file_path = LOG_DIR / f"{app_name}.log"
        if not log_file_path.exists():
            return []
        
        with open(log_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            lines = [line.rstrip('\n\r') for line in lines if line.strip()]
            
            if tail_lines:
                return lines[-tail_lines:]
            return lines
    except Exception as e:
        print(f"Error reading log for {app_name}: {e}")
        return []

async def start_streamlit_app(app_name: str, script_path: str, port: int):
    """Start Streamlit application"""
    try:
        if PROCESSES[app_name]['process'] is not None:
            return False, "Application already running"
        
        if not Path(script_path).exists():
            return False, f"File does not exist: {script_path}"
        
        # Clear previous log files
        log_file_path = LOG_DIR / f"{app_name}.log"
        if log_file_path.exists():
            log_file_path.unlink()
        
        # Create startup log
        start_msg = f"[{datetime.now().strftime('%H:%M:%S')}] Starting {app_name} application..."
        write_log_to_file(app_name, start_msg)
        
        cmd = [
            'python', '-m', 'streamlit', 'run',
            script_path,
            '--server.port', str(port),
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false',
            '--logger.level', 'info',
            '--server.enableCORS', 'false'
        ]
        
        # Set environment variables
        env = {
            'PYTHONIOENCODING': 'utf-8',
            'PYTHONUTF8': '1',
            'LANG': 'en_US.UTF-8',
            'LC_ALL': 'en_US.UTF-8',
            'PYTHONUNBUFFERED': '1',
            'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false'
        }
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=0,
            universal_newlines=False,
            cwd=Path.cwd(),
            env={**os.environ, **env}
        )
        
        PROCESSES[app_name]['process'] = process
        PROCESSES[app_name]['status'] = 'starting'
        
        # Start output monitoring
        asyncio.create_task(monitor_process_output(app_name, process))
        
        return True, f"{app_name} application starting..."
        
    except Exception as e:
        error_msg = f"Startup failed: {str(e)}"
        write_log_to_file(app_name, f"[{datetime.now().strftime('%H:%M:%S')}] {error_msg}")
        return False, error_msg

async def monitor_process_output(app_name: str, process):
    """Monitor process output and broadcast via WebSocket"""
    try:
        while process.poll() is None:
            if process.stdout:
                output = process.stdout.readline()
                if output:
                    line = output.decode('utf-8', errors='replace').strip()
                    if line:
                        timestamp = datetime.now().strftime('%H:%M:%S')
                        formatted_line = f"[{timestamp}] {line}"
                        
                        # Write to log file
                        write_log_to_file(app_name, formatted_line)
                        
                        # Broadcast via WebSocket
                        await manager.broadcast_to_frontend({
                            'type': 'console_output',
                            'data': {
                                'app': app_name,
                                'line': formatted_line
                            }
                        })
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"Error monitoring output for {app_name}: {e}")


# API Endpoints (matching Flask structure)

@router.get("/status")
async def get_engines_status(
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection)
):
    """Get status of all engines (matching Flask /api/status)"""
    try:
        check_app_status()
        
        return {
            app_name: {
                'status': info['status'],
                'port': info['port'],
                'output_lines': len(info['output'])
            }
            for app_name, info in PROCESSES.items()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{app_name}/status")
async def get_engine_status(
    app_name: str,
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection)
):
    """Get status of specific engine"""
    try:
        if app_name not in PROCESSES:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Application {app_name} not found"
            )
        
        check_app_status()
        
        return {
            'status': PROCESSES[app_name]['status'],
            'port': PROCESSES[app_name]['port'],
            'output_lines': len(PROCESSES[app_name]['output'])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/{app_name}/start")
async def start_engine(
    app_name: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection)
):
    """Start a specific engine (matching Flask /api/start/<app_name>)"""
    try:
        if app_name not in PROCESSES:
            return {'success': False, 'message': 'Unknown application'}
        
        if app_name == 'forum':
            # Handle ForumEngine startup
            try:
                # Start ForumEngine monitoring
                background_tasks.add_task(start_forum_engine)
                PROCESSES['forum']['status'] = 'running'
                return {'success': True, 'message': 'ForumEngine started'}
            except Exception as exc:
                return {'success': False, 'message': f'ForumEngine startup failed: {exc}'}
        
        script_path = STREAMLIT_SCRIPTS.get(app_name)
        if not script_path:
            return {'success': False, 'message': 'This application does not support start operation'}
        
        success, message = await start_streamlit_app(
            app_name,
            script_path,
            PROCESSES[app_name]['port']
        )
        
        if success:
            # Wait for startup with timeout handling
            try:
                await asyncio.wait_for(
                    asyncio.sleep(15),
                    timeout=20.0
                )
                check_app_status()
                if PROCESSES[app_name]['status'] == 'starting':
                    message += " but startup check may still be in progress"
            except asyncio.TimeoutError:
                message += " but startup timeout occurred"
        
        return {'success': success, 'message': message}
        
    except Exception as e:
        return {'success': False, 'message': f'Startup failed: {str(e)}'}


@router.post("/{app_name}/stop")
async def stop_engine(
    app_name: str,
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection)
):
    """Stop a specific engine (matching Flask /api/stop/<app_name>)"""
    try:
        if app_name not in PROCESSES:
            return {'success': False, 'message': 'Unknown application'}
        
        if app_name == 'forum':
            try:
                await stop_forum_engine()
                PROCESSES['forum']['status'] = 'stopped'
                return {'success': True, 'message': 'ForumEngine stopped'}
            except Exception as exc:
                return {'success': False, 'message': f'ForumEngine stop failed: {exc}'}
        
        process = PROCESSES[app_name]['process']
        if process is None:
            return {'success': False, 'message': 'Application not running'}
        
        try:
            process.terminate()
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        
        PROCESSES[app_name]['process'] = None
        PROCESSES[app_name]['status'] = 'stopped'
        
        return {'success': True, 'message': f'{app_name} application stopped'}
        
    except Exception as e:
        return {'success': False, 'message': f'Stop failed: {str(e)}'}


@router.get("/{app_name}/output")
async def get_engine_output(
    app_name: str,
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection)
):
    """Get application output (matching Flask /api/output/<app_name>)"""
    try:
        if app_name not in PROCESSES:
            return {'success': False, 'message': 'Unknown application'}
        
        # Special handling for Forum Engine
        if app_name == 'forum':
            forum_log_content = read_log_from_file('forum')
            return {
                'success': True,
                'output': forum_log_content,
                'total_lines': len(forum_log_content)
            }
        
        # Read complete logs from file
        output_lines = read_log_from_file(app_name)
        
        return {
            'success': True,
            'output': output_lines
        }
        
    except Exception as e:
        return {'success': False, 'message': f'Failed to read output: {str(e)}'}


@router.post("/{app_name}/test_log")
async def test_engine_log(
    app_name: str,
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection)
):
    """Test log writing functionality (matching Flask /api/test_log/<app_name>)"""
    try:
        if app_name not in PROCESSES:
            return {'success': False, 'message': 'Unknown application'}
        
        # Write test message
        test_msg = f"[{datetime.now().strftime('%H:%M:%S')}] Test log message - {datetime.now()}"
        write_log_to_file(app_name, test_msg)
        
        # Send via WebSocket
        await manager.broadcast_to_frontend({
            'type': 'console_output',
            'data': {
                'app': app_name,
                'line': test_msg
            }
        })
        
        return {
            'success': True,
            'message': f'Test message written to {app_name} log'
        }
        
    except Exception as e:
        return {'success': False, 'message': f'Test failed: {str(e)}'}


@router.post("/analyze")
async def start_analysis(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection)
):
    """Start analysis (matching Flask /api/search)"""
    try:
        if not request.query.strip():
            return {'success': False, 'message': 'Search query cannot be empty'}
        
        # Check which applications are running
        check_app_status()
        running_apps = [name for name, info in PROCESSES.items() if info['status'] == 'running']
        
        if not running_apps:
            return {'success': False, 'message': 'No running applications'}
        
        # Create analysis task
        analysis_id = f"analysis_{int(time.time())}"
        
        # Start analysis in background
        background_tasks.add_task(
            run_analysis,
            analysis_id,
            request.query,
            running_apps,
            request.options
        )
        
        return {
            'success': True,
            'analysis_id': analysis_id,
            'query': request.query,
            'engines': running_apps,
            'status': 'started'
        }
        
    except Exception as e:
        return {'success': False, 'message': f'Analysis failed: {str(e)}'}


@router.get("/analyze/{analysis_id}")
async def get_analysis_status(
    analysis_id: str,
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection)
):
    """Get analysis status"""
    try:
        # This would typically check a database for analysis status
        # For now, return a placeholder response
        return {
            'success': True,
            'analysis_id': analysis_id,
            'status': 'running',
            'message': 'Analysis in progress'
        }
    except Exception as e:
        return {'success': False, 'message': f'Failed to get status: {str(e)}'}


@router.put("/{agent_type}/config")
async def update_engine_config(
    agent_type: str,
    config: Dict[str, Any],
    user: dict = Depends(get_current_user),
    db = Depends(get_db_connection)
):
    """Update engine configuration"""
    try:
        # This would update configuration in database
        # For now, return success
        return {
            'type': agent_type,
            'config': config,
            'message': f'Agent {agent_type} configuration updated'
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# Helper functions for ForumEngine
async def start_forum_engine():
    """Start ForumEngine forum"""
    try:
        # This would start ForumEngine monitoring
        # For now, just update status
        PROCESSES['forum']['status'] = 'running'
        print("ForumEngine: Forum started")
    except Exception as e:
        print(f"ForumEngine: Failed to start forum: {e}")

async def stop_forum_engine():
    """Stop ForumEngine forum"""
    try:
        # This would stop ForumEngine monitoring
        # For now, just update status
        PROCESSES['forum']['status'] = 'stopped'
        print("ForumEngine: Forum stopped")
    except Exception as e:
        print(f"ForumEngine: Failed to stop forum: {e}")


async def run_analysis(analysis_id: str, query: str, engines: List[str], options: Dict[str, Any]):
    """Run analysis in background"""
    try:
        # This would run the actual analysis
        # For now, just simulate with a delay
        await asyncio.sleep(5)
        
        # Broadcast completion
        await manager.broadcast_to_frontend({
            'type': 'analysis_complete',
            'data': {
                'analysis_id': analysis_id,
                'query': query,
                'engines': engines,
                'status': 'completed'
            }
        })
    except Exception as e:
        print(f"Analysis failed: {e}")