#!/usr/bin/env python3
"""
FastAPI Backend for Test Data Environment
Main application with real-time logging and WebSocket support
"""

import os
import sys
import json
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks, Depends, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field, ValidationError
import uvicorn
from fastapi import UploadFile
import pandas as pd
import numpy as np

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import OPENAI_API_KEY, ALLOWED_ORIGINS, HOST, PORT, ENVIRONMENT
from run_id_manager import generate_run_id, list_runs, get_run_info
from schema_analyzer_agent import SchemaAnalyzerAgent
from synthetic_data_generator_agent import SyntheticDataGeneratorAgent
from test_scenario_data_generator_agent import TestScenarioDataGeneratorAgent
from validation_agent import ValidationAgent

# Import database configuration
from config import (
    MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USERNAME, MYSQL_PASSWORD,
    ORACLE_HOST, ORACLE_PORT, ORACLE_SERVICE_NAME, ORACLE_USERNAME, ORACLE_PASSWORD
)

def clean_data_for_json(df):
    """Clean DataFrame data to ensure JSON compatibility."""
    try:
        # Replace infinite values with NaN
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Fill NaN values with appropriate defaults
        df = df.fillna('')
        
        # Convert to dict with cleaned data
        cleaned_data = []
        for _, row in df.iterrows():
            cleaned_row = {}
            for col, val in row.items():
                if pd.isna(val) or val == 'nan' or val == 'None':
                    cleaned_row[col] = ''
                elif isinstance(val, (int, float)):
                    if np.isinf(val) or np.isnan(val):
                        cleaned_row[col] = 0
                    else:
                        cleaned_row[col] = val
                elif isinstance(val, (np.integer, np.floating)):
                    # Handle numpy types
                    if np.isinf(val) or np.isnan(val):
                        cleaned_row[col] = 0
                    else:
                        cleaned_row[col] = float(val) if isinstance(val, np.floating) else int(val)
                else:
                    cleaned_row[col] = str(val) if val is not None else ''
            cleaned_data.append(cleaned_row)
        
        return cleaned_data
    except Exception as e:
        logger.error(f"Error cleaning data for JSON: {e}")
        # Fallback: return empty data if cleaning fails
        return []

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Global WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {e}")
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()

# Pydantic models for API requests/responses
class RunRequest(BaseModel):
    run_id: Optional[str] = None
    mode: str = Field(default="full", description="Analysis mode: 'full' or 'schema_only'")

class DataGenerationRequest(BaseModel):
    run_id: str
    config: Dict[str, Any] = Field(default_factory=dict)

class TestScenarioRequest(BaseModel):
    run_id: str
    selected_scenarios: Optional[List[int]] = Field(default=None, description="List of scenario IDs to generate (optional)")
    config: Dict[str, Any] = Field(default_factory=dict)

class ValidationRequest(BaseModel):
    run_id: str

class RunInfo(BaseModel):
    run_id: str
    has_schema: bool
    has_synthetic_data: bool
    has_validation: bool
    has_input_data: bool
    created_at: Optional[str] = None

class LogMessage(BaseModel):
    timestamp: str
    level: str
    message: str
    run_id: Optional[str] = None
    step: Optional[str] = None

# Custom logging handler for WebSocket broadcasting
class WebSocketLogHandler(logging.Handler):
    def __init__(self, manager: ConnectionManager):
        super().__init__()
        self.manager = manager

    def emit(self, record):
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "level": record.levelname,
                "message": self.format(record),
                "run_id": getattr(record, 'run_id', None),
                "step": getattr(record, 'step', None)
            }
            
            # Broadcast log message asynchronously
            asyncio.create_task(self.manager.broadcast(json.dumps(log_entry)))
        except Exception as e:
            print(f"Error in WebSocket log handler: {e}")

# Add WebSocket handler to logger
ws_handler = WebSocketLogHandler(manager)
ws_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(ws_handler)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Test Data Environment Backend")
    yield
    # Shutdown
    logger.info("🛑 Shutting down Test Data Environment Backend")

# Create FastAPI app
app = FastAPI(
    title="Test Data Environment Backend",
    description="AI-powered synthetic data generation and validation system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket endpoint for real-time logging
@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Get all runs
@app.get("/runs", response_model=List[RunInfo])
async def get_runs():
    """Get all available runs with their status."""
    try:
        runs = list_runs()
        run_infos = []
        
        for run_id in runs:
            info = get_run_info(run_id)
            if info:
                run_infos.append(RunInfo(
                    run_id=run_id,
                    has_schema=info.get("has_schema", False),
                    has_synthetic_data=info.get("has_synthetic_data", False),
                    has_validation=info.get("has_validation", False),
                    has_input_data=info.get("has_input_data", False),
                    created_at=info.get("created_at")
                ))
        
        return run_infos
    except Exception as e:
        logger.error(f"Error getting runs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get specific run info
@app.get("/runs/{run_id}", response_model=RunInfo)
async def get_run(run_id: str):
    """Get detailed information about a specific run."""
    try:
        info = get_run_info(run_id)
        if not info:
            raise HTTPException(status_code=404, detail="Run not found")
        
        return RunInfo(
            run_id=run_id,
            has_schema=info.get("has_schema", False),
            has_synthetic_data=info.get("has_synthetic_data", False),
            has_validation=info.get("has_validation", False),
            has_input_data=info.get("has_input_data", False),
            created_at=info.get("created_at")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting run {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Schema analysis endpoint
@app.post("/schema-analysis")
async def run_schema_analysis(request: RunRequest, background_tasks: BackgroundTasks):
    """Run schema analysis for a new or existing run."""
    try:
        # Generate run ID if not provided
        run_id = request.run_id or generate_run_id()
        
        logger.info(f"🔍 Starting schema analysis for run {run_id}")
        
        # Run schema analysis in background
        background_tasks.add_task(run_schema_analysis_task, run_id, request.mode)
        
        return {
            "data": {
                "run_id": run_id,
                "status": "started",
                "message": f"Schema analysis started for run {run_id}",
                "timestamp": datetime.now().isoformat()
            },
            "status": 200
        }
    except Exception as e:
        logger.error(f"Error starting schema analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_schema_analysis_task(run_id: str, mode: str):
    """Background task for schema analysis."""
    try:
        # Add run_id to logger context
        logger.info(f"🚀 Initializing schema analyzer for run {run_id}")
        
        agent = SchemaAnalyzerAgent(api_key=OPENAI_API_KEY, run_id=run_id, mode=mode)
        
        # Run analysis
        result = agent.run_analysis()
        
        if result:
            logger.info(f"✅ Schema analysis completed successfully for run {run_id}")
            await manager.broadcast(json.dumps({
                "type": "schema_analysis_complete",
                "run_id": run_id,
                "timestamp": datetime.now().isoformat()
            }))
        else:
            logger.error(f"❌ Schema analysis failed for run {run_id}")
            await manager.broadcast(json.dumps({
                "type": "schema_analysis_failed",
                "run_id": run_id,
                "timestamp": datetime.now().isoformat()
            }))
            
    except Exception as e:
        logger.error(f"Error in schema analysis task for run {run_id}: {e}")
        await manager.broadcast(json.dumps({
            "type": "schema_analysis_error",
            "run_id": run_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))

# Synthetic data generation endpoint
@app.post("/generate-data")
async def generate_synthetic_data(request: DataGenerationRequest, background_tasks: BackgroundTasks):
    """Generate synthetic data for a run."""
    try:
        logger.info(f"🔧 Starting synthetic data generation for run {request.run_id}")
        
        # Run data generation in background
        background_tasks.add_task(run_data_generation_task, request.run_id, request.config)
        
        return {
            "data": {
                "run_id": request.run_id,
                "status": "started",
                "message": f"Synthetic data generation started for run {request.run_id}",
                "timestamp": datetime.now().isoformat()
            },
            "status": 200
        }
    except Exception as e:
        logger.error(f"Error starting data generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_data_generation_task(run_id: str, config: Dict[str, Any]):
    """Background task for synthetic data generation."""
    try:
        logger.info(f"🚀 Initializing synthetic data generator for run {run_id}")
        
        agent = SyntheticDataGeneratorAgent(api_key=OPENAI_API_KEY, run_id=run_id)
        
        # Run generation
        success = agent.run_generation(config)
        
        if success:
            logger.info(f"✅ Synthetic data generation completed successfully for run {run_id}")
            await manager.broadcast(json.dumps({
                "type": "data_generation_complete",
                "run_id": run_id,
                "timestamp": datetime.now().isoformat()
            }))
        else:
            logger.error(f"❌ Synthetic data generation failed for run {run_id}")
            await manager.broadcast(json.dumps({
                "type": "data_generation_failed",
                "run_id": run_id,
                "timestamp": datetime.now().isoformat()
            }))
            
    except Exception as e:
        logger.error(f"Error in data generation task for run {run_id}: {e}")
        await manager.broadcast(json.dumps({
            "type": "data_generation_error",
            "run_id": run_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))

# Test scenario data generation endpoint
@app.post("/generate-test-scenarios")
async def generate_test_scenario_data(request: Request, background_tasks: BackgroundTasks):
    """Generate test scenario data for a run."""
    try:
        # Log raw request data for debugging
        raw_data = await request.json()
        logger.info(f"🔍 Raw request data: {raw_data}")
        
        # Parse the request data
        try:
            parsed_request = TestScenarioRequest(**raw_data)
        except ValidationError as e:
            logger.error(f"❌ Validation error: {e}")
            logger.error(f"❌ Raw data: {raw_data}")
            raise HTTPException(status_code=422, detail=f"Validation error: {e}")
        
        logger.info(f"🧪 Starting test scenario data generation for run {parsed_request.run_id}")
        logger.info(f"📊 Parsed request data: run_id={parsed_request.run_id}, selected_scenarios={parsed_request.selected_scenarios}, config={parsed_request.config}")
        
        # Run synthetic data generation in background using SyntheticDataGeneratorAgent
        logger.info(f"🔄 Adding background task for synthetic data generation using SyntheticDataGeneratorAgent")
        background_tasks.add_task(run_synthetic_data_generation_task, parsed_request.run_id, parsed_request.config)
        logger.info(f"✅ Background task added successfully")
        
        response_data = {
            "data": {
                "run_id": parsed_request.run_id,
                "status": "started",
                "message": f"Synthetic data generation started for run {parsed_request.run_id}",
                "timestamp": datetime.now().isoformat()
            },
            "status": 200
        }
        logger.info(f"📤 Returning response: {response_data}")
        return response_data
    except Exception as e:
        logger.error(f"Error starting test scenario generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_synthetic_data_generation_task(run_id: str, config: Dict[str, Any]):
    """Background task for synthetic data generation using SyntheticDataGeneratorAgent."""
    try:
        logger.info(f"🚀 Initializing synthetic data generator for run {run_id}")
        
        from synthetic_data_generator_agent import SyntheticDataGeneratorAgent
        
        # Create the synthetic data generator agent
        agent = SyntheticDataGeneratorAgent(api_key=OPENAI_API_KEY, run_id=run_id)
        
        logger.info(f"✅ Using configuration: {config.get('default_records', 100)} default records")
        
        # Run the synthetic data generation with config
        success = agent.run_generation(config)
        
        if success:
            logger.info(f"✅ Synthetic data generation completed successfully for run {run_id}")
            await manager.broadcast(json.dumps({
                "type": "synthetic_data_generation_complete",
                "run_id": run_id,
                "timestamp": datetime.now().isoformat()
            }))
        else:
            raise Exception("Synthetic data generation failed")
            
    except Exception as e:
        logger.error(f"Error in synthetic data generation task for run {run_id}: {e}")
        await manager.broadcast(json.dumps({
            "type": "synthetic_data_generation_error",
            "run_id": run_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))

async def run_test_scenario_task(run_id: str, selected_scenarios: Optional[List[int]], config: Dict[str, Any]):
    """Background task for test scenario data generation."""
    try:
        logger.info(f"🚀 Initializing test scenario generator for run {run_id}")
        
        from test_scenario_data_generator_agent import TestScenarioDataGeneratorAgent
        
        # Create agent in non-interactive mode
        agent = TestScenarioDataGeneratorAgent(
            run_id=run_id,
            non_interactive=True,
            selected_scenarios=None,  # Will use scenarios from schema analysis
            config=config
        )
        
        # Run generation in non-interactive mode
        success = agent.run()
        
        if success:
            logger.info(f"✅ Test scenario data generation completed successfully for run {run_id}")
            await manager.broadcast(json.dumps({
                "type": "test_scenario_generation_complete",
                "run_id": run_id,
                "timestamp": datetime.now().isoformat()
            }))
        else:
            raise Exception("Test scenario data generation failed")
            
    except Exception as e:
        logger.error(f"Error in test scenario task for run {run_id}: {e}")
        await manager.broadcast(json.dumps({
            "type": "test_scenario_generation_error",
            "run_id": run_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))

# Test scenario generation endpoint
@app.post("/test-scenario-generation")
async def run_test_scenario_generation(request: RunRequest, background_tasks: BackgroundTasks):
    """Run test scenario generation for functional test scenarios product."""
    try:
        # Generate run ID if not provided
        run_id = request.run_id or generate_run_id()
        
        logger.info(f"🔍 Starting test scenario generation for run {run_id}")
        
        # Run test scenario generation in background
        background_tasks.add_task(run_test_scenario_generation_task, run_id, request.mode)
        
        return {
            "data": {
                "run_id": run_id,
                "status": "started",
                "message": f"Test scenario generation started for run {run_id}",
                "timestamp": datetime.now().isoformat()
            },
            "status": 200
        }
    except Exception as e:
        logger.error(f"Error starting test scenario generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_test_scenario_generation_task(run_id: str, mode: str):
    """Background task for test scenario generation."""
    try:
        # Add run_id to logger context
        logger.info(f"🚀 Initializing test scenario generator for run {run_id}")
        
        # For now, we'll use the business logic library generator agent instead
        # since the test scenario generator is interactive and won't work in background tasks
        from business_logic_library.library_generator_agent import LibraryGeneratorAgent
        
        logger.info(f"📚 Using business logic library generator for test scenario analysis")
        
        # Initialize the library generator agent in data analysis mode
        logger.info(f"🔧 Initializing LibraryGeneratorAgent with run_id={run_id}, mode={mode}")
        agent = LibraryGeneratorAgent(run_id=run_id, mode="data_analysis")
        
        # Run the analysis to generate business rules and test scenarios from the uploaded data
        logger.info(f"🚀 Starting agent.run() for test scenario generation...")
        result = agent.run()
        logger.info(f"📊 Agent.run() completed with result: {result}")
        
        if result:
            logger.info(f"✅ Test scenario analysis completed successfully for run {run_id}")
            await manager.broadcast(json.dumps({
                "type": "test_scenario_generation_complete",
                "run_id": run_id,
                "timestamp": datetime.now().isoformat()
            }))
        else:
            logger.error(f"❌ Test scenario analysis failed for run {run_id}")
            await manager.broadcast(json.dumps({
                "type": "test_scenario_generation_failed",
                "run_id": run_id,
                "timestamp": datetime.now().isoformat()
            }))
            
    except Exception as e:
        logger.error(f"Error in test scenario generation task for run {run_id}: {e}")
        await manager.broadcast(json.dumps({
            "type": "test_scenario_generation_error",
            "run_id": run_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))

# Generate test scenario from prompt endpoint
@app.post("/generate-scenario-from-prompt")
async def generate_scenario_from_prompt(request: dict):
    """Generate a test scenario from a user prompt using AI analysis."""
    try:
        run_id = request.get("run_id")
        table_name = request.get("table_name")
        user_prompt = request.get("user_prompt")
        
        if not all([run_id, table_name, user_prompt]):
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: run_id, table_name, user_prompt"
            )
        
        logger.info(f"🔍 Generating test scenario from prompt for run {run_id}, table {table_name}")
        logger.info(f"📝 User prompt: {user_prompt}")
        
        # Import and use the LibraryGeneratorAgent
        from business_logic_library.library_generator_agent import LibraryGeneratorAgent
        
        # Initialize the agent
        agent = LibraryGeneratorAgent(run_id=run_id, mode="data_analysis")
        
        # Generate the test scenario using the enhanced generate_from_prompt method
        business_rules, test_scenarios = agent.generate_from_prompt(user_prompt, table_name)
        
        if test_scenarios or business_rules:
            logger.info(f"✅ Successfully generated: {len(business_rules)} business rules, {len(test_scenarios)} test scenarios")
            
            # Append to library
            success = agent.append_to_library(business_rules, test_scenarios)
            if success:
                logger.info(f"✅ Successfully added generated content to library")
            else:
                logger.warning(f"⚠️ Library append failed, but content was generated")
            
            logger.info(f"📤 Returning response with {len(business_rules)} business rules and {len(test_scenarios)} test scenarios")
            response_data = {
                "data": {
                    "run_id": run_id,
                    "table_name": table_name,
                    "business_rules": business_rules,
                    "test_scenarios": test_scenarios,
                    "message": "Test scenario generated successfully",
                    "timestamp": datetime.now().isoformat()
                },
                "status": 200
            }
            logger.info(f"📤 Response structure: {json.dumps(response_data, indent=2)}")
            return response_data
        else:
            logger.warning(f"⚠️ No content generated from prompt")
            return {
                "data": {
                    "run_id": run_id,
                    "table_name": table_name,
                    "business_rules": [],
                    "test_scenarios": [],
                    "message": "No content generated from prompt",
                    "timestamp": datetime.now().isoformat()
                },
                "status": 200
            }
            
    except Exception as e:
        logger.error(f"❌ Error generating test scenario from prompt: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

# Validation endpoint
@app.post("/validate")
async def run_validation(request: ValidationRequest, background_tasks: BackgroundTasks):
    """Run validation for a run."""
    try:
        logger.info(f"🔍 Starting validation for run {request.run_id}")
        
        # Run validation in background
        background_tasks.add_task(run_validation_task, request.run_id)
        
        return {
            "run_id": request.run_id,
            "status": "started",
            "message": f"Validation started for run {request.run_id}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting validation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_validation_task(run_id: str):
    """Background task for validation."""
    try:
        logger.info(f"🚀 Initializing validation agent for run {run_id}")
        
        agent = ValidationAgent(run_id=run_id)
        
        # Run validation
        success = agent.run_validation()
        
        if success:
            logger.info(f"✅ Validation completed successfully for run {run_id}")
            await manager.broadcast(json.dumps({
                "type": "validation_complete",
                "run_id": run_id,
                "timestamp": datetime.now().isoformat()
            }))
        else:
            logger.error(f"❌ Validation failed for run {run_id}")
            await manager.broadcast(json.dumps({
                "type": "validation_failed",
                "run_id": run_id,
                "timestamp": datetime.now().isoformat()
            }))
            
    except Exception as e:
        logger.error(f"Error in validation task for run {run_id}: {e}")
        await manager.broadcast(json.dumps({
            "type": "validation_error",
            "run_id": run_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))

# Get test scenarios endpoint
@app.get("/runs/{run_id}/test-scenarios")
async def get_test_scenarios(run_id: str):
    """Get available test scenarios for a run."""
    try:
        logger.info(f"Getting test scenarios for run {run_id}")
        agent = TestScenarioDataGeneratorAgent(run_id=run_id)
        scenarios = agent.load_test_scenarios()
        
        logger.info(f"Loaded {len(scenarios)} test scenarios for run {run_id}")
        
        response = {
            "run_id": run_id,
            "scenarios": scenarios,
            "count": len(scenarios)
        }
        
        logger.info(f"Returning test scenarios response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error getting test scenarios for run {run_id}: {e}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Get run files endpoint
@app.get("/runs/{run_id}/files")
async def get_run_files(run_id: str):
    """Get list of files generated for a run."""
    try:
        run_dir = os.path.join("runs", run_id)
        if not os.path.exists(run_dir):
            raise HTTPException(status_code=404, detail="Run not found")
        
        logger.info(f"🔍 Scanning files for run {run_id} in directory: {run_dir}")
        
        files = {}
        
        # Check each directory
        directories = {
            "schema": os.path.join(run_dir, "schema"),
            "synthetic_data": os.path.join(run_dir, "synthetic_data", "data"),
            "validation": os.path.join(run_dir, "validation", "reports"),
            "scripts": os.path.join(run_dir, "synthetic_data", "scripts")
        }
        
        for dir_name, dir_path in directories.items():
            logger.info(f"🔍 Checking directory: {dir_name} -> {dir_path}")
            if os.path.exists(dir_path):
                files[dir_name] = []
                dir_files = os.listdir(dir_path)
                logger.info(f"📁 Found {len(dir_files)} files in {dir_name}: {dir_files}")
                
                for file in dir_files:
                    if file.endswith(('.csv', '.json', '.txt', '.py')):
                        file_path = os.path.join(dir_path, file)
                        file_stat = os.stat(file_path)
                        file_info = {
                            "name": file,
                            "size": file_stat.st_size,
                            "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                        }
                        files[dir_name].append(file_info)
                        logger.info(f"📄 Added file: {file} (size: {file_stat.st_size} bytes)")
            else:
                logger.warning(f"⚠️ Directory not found: {dir_path}")
        
        logger.info(f"📊 Total files found for run {run_id}: {sum(len(files.get(k, [])) for k in files)}")
        return {
            "run_id": run_id,
            "files": files
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting files for run {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Download file endpoint
@app.get("/runs/{run_id}/files/{file_type}/{filename}")
async def download_file(run_id: str, file_type: str, filename: str):
    """Download a specific file from a run."""
    try:
        run_dir = os.path.join("runs", run_id)
        if not os.path.exists(run_dir):
            raise HTTPException(status_code=404, detail="Run not found")
        
        # Map file types to directories
        dir_mapping = {
            "schema": os.path.join(run_dir, "schema"),
            "synthetic_data": os.path.join(run_dir, "synthetic_data", "data"),
            "validation": os.path.join(run_dir, "validation", "reports"),
            "scripts": os.path.join(run_dir, "synthetic_data", "scripts")
        }
        
        if file_type not in dir_mapping:
            raise HTTPException(status_code=400, detail="Invalid file type")
        
        file_path = os.path.join(dir_mapping[file_type], filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Return file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {
            "run_id": run_id,
            "file_type": file_type,
            "filename": filename,
            "content": content
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file {filename} for run {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Get run configuration endpoint
@app.get("/runs/{run_id}/config")
async def get_run_config(run_id: str):
    """Get the run configuration file for a specific run."""
    try:
        run_dir = os.path.join("runs", run_id)
        if not os.path.exists(run_dir):
            raise HTTPException(status_code=404, detail="Run not found")
        
        config_file = os.path.join(run_dir, "run_config.json")
        if not os.path.exists(config_file):
            raise HTTPException(status_code=404, detail="Run configuration not found")
        
        # Return run configuration
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        return {
            "run_id": run_id,
            "config": config
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading run configuration for run {run_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# List files in input_data directory
@app.get("/input_data")
async def list_input_data_files():
    """List all CSV files in the input_data directory."""
    try:
        input_data_dir = "input_data"
        if not os.path.exists(input_data_dir):
            return []
        
        files = []
        for filename in os.listdir(input_data_dir):
            if filename.endswith('.csv'):
                file_path = os.path.join(input_data_dir, filename)
                file_stat = os.stat(file_path)
                files.append({
                    "name": filename,
                    "size": file_stat.st_size,
                    "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                })
        
        return files
    except Exception as e:
        logger.error(f"Error listing input_data files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# List files in input_schemas directory
@app.get("/input_schemas")
async def list_input_schemas_files():
    """List all CSV files in the input_schemas directory."""
    try:
        input_schemas_dir = "input_schemas"
        if not os.path.exists(input_schemas_dir):
            return []
        
        files = []
        for filename in os.listdir(input_schemas_dir):
            if filename.endswith('.csv'):
                file_path = os.path.join(input_schemas_dir, filename)
                file_stat = os.stat(file_path)
                files.append({
                    "name": filename,
                    "size": file_stat.st_size,
                    "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                })
        
        return files
    except Exception as e:
        logger.error(f"Error listing input_schemas files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve CSV files from input_data directory
@app.get("/input_data/{filename}")
async def serve_input_data_file(filename: str):
    """Serve a specific CSV file from the input_data directory."""
    try:
        file_path = os.path.join("input_data", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Return file content with proper content type
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        from fastapi.responses import Response
        return Response(content=content, media_type="text/csv")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving input_data file {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Serve CSV files from input_schemas directory
@app.get("/input_schemas/{filename}")
async def serve_input_schemas_file(filename: str):
    """Serve a specific CSV file from the input_schemas directory."""
    try:
        file_path = os.path.join("input_schemas", filename)
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Return file content with proper content type
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        from fastapi.responses import Response
        return Response(content=content, media_type="text/csv")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving input_schemas file {filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Complete pipeline endpoint
@app.post("/pipeline/complete")
async def run_complete_pipeline(request: RunRequest, background_tasks: BackgroundTasks):
    """Run the complete pipeline: schema analysis, data generation, and validation."""
    try:
        run_id = request.run_id or generate_run_id()
        
        logger.info(f"🚀 Starting complete pipeline for run {run_id}")
        
        # Run complete pipeline in background
        background_tasks.add_task(run_complete_pipeline_task, run_id, request.mode)
        
        return {
            "run_id": run_id,
            "status": "started",
            "message": f"Complete pipeline started for run {run_id}",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error starting complete pipeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Test MySQL connection
@app.post("/test-mysql-connection")
async def test_mysql_connection(request: dict):
    """Test MySQL database connection."""
    try:
        import mysql.connector
        from mysql.connector import Error
        
        connection_params = {
            'host': request.get('host', MYSQL_HOST),
            'port': int(request.get('port', MYSQL_PORT)),
            'database': request.get('database', MYSQL_DATABASE),
            'user': request.get('username', MYSQL_USERNAME),
            'password': request.get('password', MYSQL_PASSWORD)
        }
        
        # Test connection
        connection = mysql.connector.connect(**connection_params)
        
        if connection.is_connected():
            db_info = connection.get_server_info()
            cursor = connection.cursor()
            cursor.execute("select database();")
            db_name = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            logger.info(f"MySQL connection successful to {db_name} on {connection_params['host']}")
            
            return {
                "status": "success",
                "message": f"Connected to MySQL database '{db_name}' on {connection_params['host']}",
                "server_info": db_info
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to establish MySQL connection")
            
    except Error as e:
        logger.error(f"MySQL connection error: {e}")
        raise HTTPException(status_code=500, detail=f"MySQL connection failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error testing MySQL connection: {e}")
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")

# Test Oracle connection
@app.post("/test-oracle-connection")
async def test_oracle_connection(request: dict):
    """Test Oracle database connection."""
    try:
        # Try to import cx_Oracle, but handle the case where it's not installed
        try:
            import cx_Oracle
        except ImportError:
            logger.error("cx_Oracle module not found. Please install it with: pip install cx-Oracle")
            raise HTTPException(
                status_code=500, 
                detail="Oracle client library not installed. Please install cx-Oracle: pip install cx-Oracle"
            )
        
        connection_params = {
            'user': request.get('username', ORACLE_USERNAME),
            'password': request.get('password', ORACLE_PASSWORD),
            'dsn': f"{request.get('host', ORACLE_HOST)}:{request.get('port', ORACLE_PORT)}/{request.get('serviceName', ORACLE_SERVICE_NAME)}"
        }
        
        # Test connection
        connection = cx_Oracle.connect(**connection_params)
        
        if connection:
            cursor = connection.cursor()
            cursor.execute("SELECT sys_context('USERENV', 'DB_NAME') FROM dual")
            db_name = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            logger.info(f"Oracle connection successful to {db_name} on {request.get('host', ORACLE_HOST)}")
            
            return {
                "status": "success",
                "message": f"Connected to Oracle database '{db_name}' on {request.get('host', ORACLE_HOST)}",
                "database_name": db_name
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to establish Oracle connection")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Oracle connection error: {e}")
        raise HTTPException(status_code=500, detail=f"Oracle connection failed: {str(e)}")

def create_run_config(run_id: str, product_type: str, source_type: str, details: dict) -> dict:
    """Create a run configuration file with all the details for the run."""
    config = {
        "run_id": run_id,
        "created_at": datetime.now().isoformat(),
        "product_type": product_type,
        "source_type": source_type,
        "source_details": details,
        "folder_structure": {
            "run_dir": f"runs/{run_id}",
            "input_data_dir": f"runs/{run_id}/input_data",
            "target_subdir": f"runs/{run_id}/input_data/{'schema' if product_type == 'synthetic-data-generation' else 'data'}",
            "schema_dir": f"runs/{run_id}/schema",
            "synthetic_data_dir": f"runs/{run_id}/synthetic_data",
            "validation_dir": f"runs/{run_id}/validation"
        },
        "analysis_mode": "full" if product_type == "synthetic-data-generation" else "schema_only",
        "status": {
            "has_input_data": True,
            "has_schema": False,
            "has_synthetic_data": False,
            "has_validation": False
        },
        "files": [],
        "metadata": {
            "description": f"Run for {product_type} using {source_type}",
            "total_files": 0,
            "total_rows": 0
        }
    }
    
    # Save config to run directory
    run_dir = f"runs/{run_id}"
    os.makedirs(run_dir, exist_ok=True)
    
    config_file_path = os.path.join(run_dir, "run_config.json")
    with open(config_file_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Created run configuration file: {config_file_path}")
    return config

# Upload files
@app.post("/upload-files")
async def upload_files(files: List[UploadFile], product_type: str = Form("functional-test-scenarios")):
    """Upload and process CSV files."""
    try:
        # Generate run ID first
        run_id = generate_run_id()
        
        # Create run directory structure based on product type
        run_dir = f"runs/{run_id}"
        input_data_dir = f"runs/{run_id}/input_data"
        
        # Determine the correct subdirectory based on product type
        if product_type == "synthetic-data-generation":
            # For synthetic data generation: save to input_data/schema
            target_dir = f"{input_data_dir}/schema"
            folder_purpose = "schema files for synthetic data generation"
        else:
            # For functional test scenarios: save to input_data/data
            target_dir = f"{input_data_dir}/data"
            folder_purpose = "data files for functional test scenarios"
        
        # Create the directory structure
        os.makedirs(target_dir, exist_ok=True)
        
        uploaded_data = {}
        total_rows = 0
        
        for file in files:
            if not file.filename.endswith('.csv'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a CSV file")
            
            logger.info(f"Processing file: {file.filename}")
            
            # Read CSV content
            content = await file.read()
            csv_text = content.decode('utf-8')
            
            # Save file to the specific run's target directory
            file_path = os.path.join(target_dir, file.filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(csv_text)
            
            # Parse CSV data
            import pandas as pd
            import io
            
            df = pd.read_csv(io.StringIO(csv_text))
            total_rows += len(df)
            
            logger.info(f"Loaded CSV {file.filename}: {len(df)} rows, {len(df.columns)} columns")
            
            # Check for problematic data types
            for col in df.columns:
                col_dtype = df[col].dtype
                if col_dtype == 'object':
                    # Check for problematic string values
                    problematic_values = df[col].isin(['inf', '-inf', 'nan', 'None', 'NULL']).sum()
                    if problematic_values > 0:
                        logger.warning(f"Column {col} in {file.filename} has {problematic_values} problematic values")
                elif col_dtype in ['float64', 'float32']:
                    # Check for infinite or NaN values
                    inf_count = np.isinf(df[col]).sum()
                    nan_count = np.isnan(df[col]).sum()
                    if inf_count > 0 or nan_count > 0:
                        logger.warning(f"Column {col} in {file.filename} has {inf_count} inf and {nan_count} NaN values")
            
            # Clean the data: replace non-JSON-compliant values
            df = df.replace([np.inf, -np.inf], np.nan)
            df = df.fillna('')
            
            logger.info(f"Cleaned data for {file.filename}")
            
            # Store the data with cleaned values
            table_name = file.filename.replace('.csv', '')
            
            # Convert to dict with cleaned data for JSON response
            cleaned_data = clean_data_for_json(df)
            
            logger.info(f"Converted {file.filename} to cleaned dict with {len(cleaned_data)} records")
            
            uploaded_data[table_name] = {
                'filename': file.filename,
                'columns': df.columns.tolist(),
                'row_count': len(df),
                'data': cleaned_data
            }
            
            logger.info(f"Uploaded and saved {file.filename} with {len(df)} rows and {len(df.columns)} columns to run {run_id} at {file_path} ({folder_purpose})")
        
        # Create run configuration file
        run_config = create_run_config(
            run_id=run_id,
            product_type=product_type,
            source_type="file_upload",
            details={
                "uploaded_files": [f.filename for f in files],
                "total_files": len(files),
                "total_rows": total_rows,
                "target_directory": target_dir,
                "folder_purpose": folder_purpose
            }
        )
        
        # Update config with file details
        run_config["files"] = list(uploaded_data.keys())
        run_config["metadata"]["total_files"] = len(files)
        run_config["metadata"]["total_rows"] = total_rows
        
        # Save updated config
        config_file_path = os.path.join(run_dir, "run_config.json")
        with open(config_file_path, 'w', encoding='utf-8') as f:
            json.dump(run_config, f, indent=2, ensure_ascii=False)
        
        # Final safety check: ensure the response can be serialized to JSON
        try:
            response_data = {
                "status": "success",
                "message": f"Successfully uploaded {len(files)} file(s) to run {run_id} in {folder_purpose}",
                "run_id": run_id,
                "product_type": product_type,
                "target_directory": target_dir,
                "files": uploaded_data,
                "run_config": run_config
            }
            
            # Test JSON serialization
            json.dumps(response_data)
            
            return response_data
        except Exception as json_error:
            logger.error(f"JSON serialization error in file upload: {json_error}")
            # Return a simplified response if full data can't be serialized
            return {
                "status": "success",
                "message": f"Successfully uploaded {len(files)} file(s) to run {run_id} in {folder_purpose}",
                "run_id": run_id,
                "product_type": product_type,
                "target_directory": target_dir,
                "files_uploaded": list(uploaded_data.keys()),
                "total_files": len(files),
                "total_rows": total_rows
            }
        
    except Exception as e:
        logger.error(f"File upload error: {e}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

# Load MySQL data
@app.post("/load-mysql-data")
async def load_mysql_data(request: dict, product_type: str = "functional-test-scenarios"):
    """Load data from MySQL database."""
    try:
        import mysql.connector
        import pandas as pd
        import os
        
        # Generate run ID first
        run_id = generate_run_id()
        
        # Create run directory structure based on product type
        run_dir = f"runs/{run_id}"
        input_data_dir = f"runs/{run_id}/input_data"
        
        # Determine the correct subdirectory based on product type
        if product_type == "synthetic-data-generation":
            # For synthetic data generation: save to input_data/schema
            target_dir = f"{input_data_dir}/schema"
            folder_purpose = "schema files for synthetic data generation"
        else:
            # For functional test scenarios: save to input_data/data
            target_dir = f"{input_data_dir}/data"
            folder_purpose = "data files for functional test scenarios"
        
        # Create the directory structure
        os.makedirs(target_dir, exist_ok=True)
        
        connection_params = {
            'host': request.get('host', MYSQL_HOST),
            'port': int(request.get('port', MYSQL_PORT)),
            'database': request.get('database', MYSQL_DATABASE),
            'user': request.get('username', MYSQL_USERNAME),
            'password': request.get('password', MYSQL_PASSWORD)
        }
        
        # Connect to MySQL
        connection = mysql.connector.connect(**connection_params)
        
        if not connection.is_connected():
            raise HTTPException(status_code=500, detail="Failed to connect to MySQL")
        
        cursor = connection.cursor()
        
        # Get list of tables
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        loaded_data = {}
        total_rows = 0
        
        # Load data from each table
        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                if rows:
                    # Get column names
                    cursor.execute(f"DESCRIBE {table}")
                    columns = [col[0] for col in cursor.fetchall()]
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(rows, columns=columns)
                    total_rows += len(rows)
                    
                    logger.info(f"Processing table {table} with {len(rows)} rows and {len(columns)} columns")
                    
                    # Clean the data: replace non-JSON-compliant values
                    df = df.replace([np.inf, -np.inf], np.nan)
                    df = df.fillna('')
                    
                    # Save as CSV file to the specific run's target directory
                    csv_filename = f"{table}.csv"
                    csv_path = os.path.join(target_dir, csv_filename)
                    df.to_csv(csv_path, index=False)
                    
                    # Convert to dict with cleaned data for JSON response
                    cleaned_data = clean_data_for_json(df)
                    
                    loaded_data[table] = {
                        'columns': columns,
                        'row_count': len(rows),
                        'data': cleaned_data
                    }
                    
                    logger.info(f"Loaded and saved {len(rows)} rows from MySQL table {table} to run {run_id} at {csv_path} ({folder_purpose})")
                else:
                    logger.info(f"Table {table} is empty, skipping")
            except Exception as table_error:
                logger.error(f"Error processing table {table}: {table_error}")
                continue
        
        cursor.close()
        connection.close()
        
        # Create run configuration file
        run_config = create_run_config(
            run_id=run_id,
            product_type=product_type,
            source_type="mysql_database",
            details={
                "connection_params": {k: v for k, v in connection_params.items() if k != 'password'},
                "database_name": connection_params['database'],
                "tables_loaded": list(loaded_data.keys()),
                "total_tables": len(loaded_data),
                "total_rows": total_rows,
                "target_directory": target_dir,
                "folder_purpose": folder_purpose
            }
        )
        
        # Update config with table details
        run_config["files"] = list(loaded_data.keys())
        run_config["metadata"]["total_files"] = len(loaded_data)
        run_config["metadata"]["total_rows"] = total_rows
        
        # Save updated config
        config_file_path = os.path.join(run_dir, "run_config.json")
        with open(config_file_path, 'w', encoding='utf-8') as f:
            json.dump(run_config, f, indent=2, ensure_ascii=False)
        
        # Final safety check: ensure the response can be serialized to JSON
        try:
            response_data = {
                "status": "success",
                "message": f"Successfully loaded data from {len(loaded_data)} MySQL tables to run {run_id} in {folder_purpose}",
                "run_id": run_id,
                "product_type": product_type,
                "target_directory": target_dir,
                "tables": loaded_data,
                "run_config": run_config
            }
            
            # Test JSON serialization
            json.dumps(response_data)
            
            return response_data
        except Exception as json_error:
            logger.error(f"JSON serialization error: {json_error}")
            # Return a simplified response if full data can't be serialized
            return {
                "status": "success",
                "message": f"Successfully loaded data from {len(loaded_data)} MySQL tables to run {run_id} in {folder_purpose}",
                "run_id": run_id,
                "product_type": product_type,
                "target_directory": target_dir,
                "tables_loaded": list(loaded_data.keys()),
                "total_tables": len(loaded_data),
                "total_rows": total_rows
            }
        
    except Exception as e:
        logger.error(f"MySQL data loading error: {e}")
        raise HTTPException(status_code=500, detail=f"MySQL data loading failed: {str(e)}")

# Load Oracle data
@app.post("/load-oracle-data")
async def load_oracle_data(request: dict, product_type: str = "functional-test-scenarios"):
    """Load data from Oracle database."""
    try:
        # Try to import cx_Oracle, but handle the case where it's not installed
        try:
            import cx_Oracle
        except ImportError:
            logger.error("cx_Oracle module not found. Please install it with: pip install cx-Oracle")
            raise HTTPException(
                status_code=500, 
                detail="Oracle client library not installed. Please install cx-Oracle: pip install cx-Oracle"
            )
        
        import pandas as pd
        import os
        
        # Generate run ID first
        run_id = generate_run_id()
        
        # Create run directory structure based on product type
        run_dir = f"runs/{run_id}"
        input_data_dir = f"runs/{run_id}/input_data"
        
        # Determine the correct subdirectory based on product type
        if product_type == "synthetic-data-generation":
            # For synthetic data generation: save to input_data/schema
            target_dir = f"{input_data_dir}/schema"
            folder_purpose = "schema files for synthetic data generation"
        else:
            # For functional test scenarios: save to input_data/data
            target_dir = f"{input_data_dir}/data"
            folder_purpose = "data files for functional test scenarios"
        
        # Create the directory structure
        os.makedirs(target_dir, exist_ok=True)
        
        connection_params = {
            'user': request.get('username', ORACLE_USERNAME),
            'password': request.get('password', ORACLE_PASSWORD),
            'dsn': f"{request.get('host', ORACLE_HOST)}:{request.get('port', ORACLE_PORT)}/{request.get('serviceName', ORACLE_SERVICE_NAME)}"
        }
        
        # Connect to Oracle
        connection = cx_Oracle.connect(**connection_params)
        
        if not connection:
            raise HTTPException(status_code=500, detail="Failed to connect to Oracle")
        
        cursor = connection.cursor()
        
        # Get list of tables accessible to the user
        cursor.execute("""
            SELECT table_name 
            FROM user_tables 
            ORDER BY table_name
        """)
        tables = [table[0] for table in cursor.fetchall()]
        
        loaded_data = {}
        total_rows = 0
        
        # Load data from each table
        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                
                if rows:
                    # Get column names
                    columns = [col[0] for col in cursor.description]
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(rows, columns=columns)
                    total_rows += len(rows)
                    
                    # Clean the data: replace non-JSON-compliant values
                    df = df.replace([np.inf, -np.inf], np.nan)
                    df = df.fillna('')
                    
                    # Save as CSV file to the specific run's target directory
                    csv_filename = f"{table}.csv"
                    csv_path = os.path.join(target_dir, csv_filename)
                    df.to_csv(csv_path, index=False)
                    
                    # Convert to dict with cleaned data for JSON response
                    cleaned_data = clean_data_for_json(df)
                    
                    loaded_data[table] = {
                        'columns': columns,
                        'row_count': len(rows),
                        'data': cleaned_data
                    }
                    
                    logger.info(f"Loaded and saved {len(rows)} rows from Oracle table {table} to run {run_id} at {csv_path} ({folder_purpose})")
            except Exception as table_error:
                logger.warning(f"Could not load table {table}: {table_error}")
                continue
        
        cursor.close()
        connection.close()
        
        # Create run configuration file
        run_config = create_run_config(
            run_id=run_id,
            product_type=product_type,
            source_type="oracle_database",
            details={
                "connection_params": {k: v for k, v in connection_params.items() if k != 'password'},
                "dsn": connection_params['dsn'],
                "tables_loaded": list(loaded_data.keys()),
                "total_tables": len(loaded_data),
                "total_rows": total_rows,
                "target_directory": target_dir,
                "folder_purpose": folder_purpose
            }
        )
        
        # Final safety check: ensure the response can be serialized to JSON
        try:
            response_data = {
                "status": "success",
                "message": f"Successfully loaded data from Oracle database to run {run_id}",
                "run_id": run_id,
                "tables_loaded": list(loaded_data.keys()),
                "total_tables": len(loaded_data),
                "total_rows": total_rows,
                "target_directory": target_dir,
                "folder_purpose": folder_purpose
            }
            
            # Test JSON serialization
            json.dumps(response_data)
            
            return response_data
        except Exception as json_error:
            logger.error(f"JSON serialization error: {json_error}")
            # Return a simplified response if full data can't be serialized
            return {
                "status": "success",
                "message": f"Successfully loaded data from Oracle database to run {run_id}",
                "run_id": run_id,
                "tables_loaded": list(loaded_data.keys()),
                "total_tables": len(loaded_data),
                "total_rows": total_rows,
                "target_directory": target_dir,
                "folder_purpose": folder_purpose
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading Oracle data: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading Oracle data: {str(e)}")

async def run_complete_pipeline_task(run_id: str, mode: str):
    """Background task for complete pipeline."""
    try:
        logger.info(f"🚀 Running complete pipeline for run {run_id}")
        
        # Import and run the complete pipeline
        from run_complete_pipeline import run_complete_pipeline
        
        success = run_complete_pipeline(run_id=run_id, mode=mode)
        
        if success:
            logger.info(f"✅ Complete pipeline finished successfully for run {run_id}")
            await manager.broadcast(json.dumps({
                "type": "pipeline_complete",
                "run_id": run_id,
                "timestamp": datetime.now().isoformat()
            }))
        else:
            logger.error(f"❌ Complete pipeline failed for run {run_id}")
            await manager.broadcast(json.dumps({
                "type": "pipeline_failed",
                "run_id": run_id,
                "timestamp": datetime.now().isoformat()
            }))
            
    except Exception as e:
        logger.error(f"Error in complete pipeline task for run {run_id}: {e}")
        await manager.broadcast(json.dumps({
            "type": "pipeline_error",
            "run_id": run_id,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }))

# Push data to database endpoint
@app.post("/push-data-to-database")
async def push_data_to_database(request: dict):
    """Push generated data to MySQL or Oracle database."""
    try:
        run_id = request.get("run_id")
        database_type = request.get("database_type")
        connection = request.get("connection")
        files = request.get("files", [])
        
        if not run_id or not database_type or not connection:
            raise HTTPException(status_code=400, detail="Missing required parameters")
        
        run_dir = os.path.join("runs", run_id)
        if not os.path.exists(run_dir):
            raise HTTPException(status_code=404, detail="Run not found")
        
        # Get the synthetic data directory
        synthetic_data_dir = os.path.join(run_dir, "synthetic_data", "data")
        if not os.path.exists(synthetic_data_dir):
            raise HTTPException(status_code=404, detail="No synthetic data found for this run")
        
        logger.info(f"Pushing data to {database_type} database for run {run_id}")
        
        if database_type == "mysql":
            return await push_to_mysql(connection, synthetic_data_dir, files)
        elif database_type == "oracle":
            return await push_to_oracle(connection, synthetic_data_dir, files)
        else:
            raise HTTPException(status_code=400, detail="Unsupported database type")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pushing data to database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def push_to_mysql(connection: dict, data_dir: str, files: list):
    """Push data to MySQL database."""
    try:
        import mysql.connector
        from mysql.connector import Error
        
        # Connect to MySQL
        conn = mysql.connector.connect(
            host=connection.get("host", "localhost"),
            port=int(connection.get("port", 3306)),
            database=connection.get("database"),
            user=connection.get("username"),
            password=connection.get("password")
        )
        
        if conn.is_connected():
            cursor = conn.cursor()
            
            # Process each CSV file
            for file_info in files:
                file_path = os.path.join(data_dir, file_info["name"])
                if os.path.exists(file_path):
                    table_name = file_info["name"].replace(".csv", "").lower()
                    
                    # Read CSV file
                    df = pd.read_csv(file_path)
                    
                    # Clean the data: replace NaN values with appropriate defaults based on data type
                    for col in df.columns:
                        col_dtype = df[col].dtype
                        if col_dtype == 'int64':
                            df[col] = df[col].fillna(0)
                        elif col_dtype == 'float64':
                            df[col] = df[col].fillna(0.0)
                        elif col_dtype == 'bool':
                            df[col] = df[col].fillna(False)
                        elif col_dtype == 'datetime64[ns]':
                            df[col] = df[col].fillna(pd.NaT)
                        else:
                            # For string/object columns, replace NaN with empty string
                            df[col] = df[col].fillna('')
                    
                    # Create table if not exists
                    columns = []
                    for col in df.columns:
                        col_type = "VARCHAR(255)"  # Default type
                        if df[col].dtype == 'int64':
                            col_type = "INT"
                        elif df[col].dtype == 'float64':
                            col_type = "DOUBLE"
                        elif df[col].dtype == 'bool':
                            col_type = "BOOLEAN"
                        elif df[col].dtype == 'datetime64[ns]':
                            col_type = "DATETIME"
                        columns.append(f"`{col}` {col_type}")
                    
                    create_table_sql = f"""
                    CREATE TABLE IF NOT EXISTS `{table_name}` (
                        {', '.join(columns)}
                    )
                    """
                    cursor.execute(create_table_sql)
                    
                    # Insert data with proper value handling
                    for _, row in df.iterrows():
                        # Convert row values to a list, handling NaN and None values
                        values = []
                        for col, val in row.items():
                            col_dtype = df[col].dtype
                            
                            if pd.isna(val) or val == 'nan' or val == 'None':
                                # Handle missing values based on column type
                                if col_dtype == 'int64':
                                    values.append(0)
                                elif col_dtype == 'float64':
                                    values.append(0.0)
                                elif col_dtype == 'bool':
                                    values.append(False)
                                elif col_dtype == 'datetime64[ns]':
                                    values.append(None)  # Use NULL for datetime
                                else:
                                    values.append('')  # Empty string for text
                            elif isinstance(val, (int, float)) and pd.isna(val):
                                # Handle numeric NaN values
                                if col_dtype == 'int64':
                                    values.append(0)
                                elif col_dtype == 'float64':
                                    values.append(0.0)
                                else:
                                    values.append(None)
                            else:
                                # Handle empty strings in numeric columns
                                if col_dtype in ['int64', 'float64'] and val == '':
                                    if col_dtype == 'int64':
                                        values.append(0)
                                    else:
                                        values.append(0.0)
                                else:
                                    values.append(val)
                        
                        placeholders = ', '.join(['%s'] * len(values))
                        insert_sql = f"INSERT INTO `{table_name}` VALUES ({placeholders})"
                        cursor.execute(insert_sql, tuple(values))
                    
                    logger.info(f"Inserted {len(df)} records into table {table_name}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Data successfully pushed to MySQL database",
                "tables_created": len(files)
            }
            
    except Error as e:
        logger.error(f"MySQL Error: {e}")
        raise HTTPException(status_code=500, detail=f"MySQL Error: {e}")
    except Exception as e:
        logger.error(f"Error pushing to MySQL: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def push_to_oracle(connection: dict, data_dir: str, files: list):
    """Push data to Oracle database."""
    try:
        # Try to import cx_Oracle, but handle the case where it's not installed
        try:
            import cx_Oracle
        except ImportError:
            logger.error("cx_Oracle module not found. Please install it with: pip install cx-Oracle")
            raise HTTPException(
                status_code=500, 
                detail="Oracle client library not installed. Please install cx-Oracle: pip install cx-Oracle"
            )
        
        # Connect to Oracle
        dsn = cx_Oracle.makedsn(
            connection.get("host", "localhost"),
            int(connection.get("port", 1521)),
            service_name=connection.get("serviceName")
        )
        
        conn = cx_Oracle.connect(
            user=connection.get("username"),
            password=connection.get("password"),
            dsn=dsn
        )
        
        if conn:
            cursor = conn.cursor()
            
            # Process each CSV file
            for file_info in files:
                file_path = os.path.join(data_dir, file_info["name"])
                if os.path.exists(file_path):
                    table_name = file_info["name"].replace(".csv", "").upper()
                    
                    # Read CSV file
                    df = pd.read_csv(file_path)
                    
                    # Clean the data: replace NaN values with appropriate defaults based on data type
                    for col in df.columns:
                        col_dtype = df[col].dtype
                        if col_dtype == 'int64':
                            df[col] = df[col].fillna(0)
                        elif col_dtype == 'float64':
                            df[col] = df[col].fillna(0.0)
                        elif col_dtype == 'bool':
                            df[col] = df[col].fillna(False)
                        elif col_dtype == 'datetime64[ns]':
                            df[col] = df[col].fillna(pd.NaT)
                        else:
                            # For string/object columns, replace NaN with empty string
                            df[col] = df[col].fillna('')
                    
                    # Create table if not exists
                    columns = []
                    for col in df.columns:
                        col_type = "VARCHAR2(255)"  # Default type
                        if df[col].dtype == 'int64':
                            col_type = "NUMBER"
                        elif df[col].dtype == 'float64':
                            col_type = "NUMBER"
                        elif df[col].dtype == 'bool':
                            col_type = "NUMBER(1)"  # Oracle uses NUMBER(1) for boolean
                        elif df[col].dtype == 'datetime64[ns]':
                            col_type = "DATE"
                        columns.append(f'"{col}" {col_type}')
                    
                    create_table_sql = f"""
                    CREATE TABLE {table_name} (
                        {', '.join(columns)}
                    )
                    """
                    try:
                        cursor.execute(create_table_sql)
                    except cx_Oracle.DatabaseError as e:
                        # Table might already exist, continue
                        pass
                    
                    # Insert data with proper value handling
                    for _, row in df.iterrows():
                        # Convert row values to a list, handling NaN and None values
                        values = []
                        for col, val in row.items():
                            col_dtype = df[col].dtype
                            
                            if pd.isna(val) or val == 'nan' or val == 'None':
                                # Handle missing values based on column type
                                if col_dtype == 'int64':
                                    values.append(0)
                                elif col_dtype == 'float64':
                                    values.append(0.0)
                                elif col_dtype == 'bool':
                                    values.append(False)
                                elif col_dtype == 'datetime64[ns]':
                                    values.append(None)  # Use NULL for datetime
                                else:
                                    values.append('')  # Empty string for text
                            elif isinstance(val, (int, float)) and pd.isna(val):
                                # Handle numeric NaN values
                                if col_dtype == 'int64':
                                    values.append(0)
                                elif col_dtype == 'float64':
                                    values.append(0.0)
                                else:
                                    values.append(None)
                            else:
                                # Handle empty strings in numeric columns
                                if col_dtype in ['int64', 'float64'] and val == '':
                                    if col_dtype == 'int64':
                                        values.append(0)
                                    else:
                                        values.append(0.0)
                                else:
                                    values.append(val)
                        
                        placeholders = ', '.join([':' + str(i+1) for i in range(len(values))])
                        insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                        cursor.execute(insert_sql, tuple(values))
                    
                    logger.info(f"Inserted {len(df)} records into table {table_name}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return {
                "status": "success",
                "message": f"Data successfully pushed to Oracle database",
                "tables_created": len(files)
            }
            
    except HTTPException:
        raise
    except cx_Oracle.DatabaseError as e:
        logger.error(f"Oracle Error: {e}")
        raise HTTPException(status_code=500, detail=f"Oracle Error: {e}")
    except Exception as e:
        logger.error(f"Error pushing to Oracle: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=True,
        log_level="info"
    ) 