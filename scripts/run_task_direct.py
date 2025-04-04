#!/usr/bin/env python
"""
Direct task execution script for Airflow tasks when Celery worker fails

This script allows direct execution of an Airflow task without going through the Celery executor.
Run this script directly on the worker node to execute a task.

Usage:
    python run_task_direct.py <dag_id> <task_id> <execution_date>

Example:
    python run_task_direct.py video_kpi_processor run_video_kpi_script 2025-04-03T12:00:00
"""
import os
import sys
import importlib.util
import datetime
from pathlib import Path

def setup_environment():
    """Set up the Airflow environment"""
    # Add current directory to path
    sys.path.insert(0, os.getcwd())
    
    # Set necessary Airflow environment variables
    os.environ['AIRFLOW__CORE__DAGS_FOLDER'] = '/opt/airflow/dags'
    
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print(f"User: {os.getuid()}:{os.getgid()}")

def import_dag_file(dag_id):
    """Import the DAG file containing the specified DAG ID"""
    dags_folder = os.environ.get('AIRFLOW__CORE__DAGS_FOLDER', '/opt/airflow/dags')
    dag_files = list(Path(dags_folder).glob('*.py'))
    
    for dag_file in dag_files:
        try:
            print(f"Checking {dag_file}...")
            # Read file to find DAG ID
            with open(dag_file, 'r') as f:
                content = f.read()
                if f"'{dag_id}'" in content or f'"{dag_id}"' in content:
                    print(f"Found DAG {dag_id} in file {dag_file}")
                    # Import the module
                    spec = importlib.util.spec_from_file_location("dag_module", dag_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module
        except Exception as e:
            print(f"Error checking file {dag_file}: {e}")
    
    raise ValueError(f"Could not find DAG {dag_id} in any file in {dags_folder}")

def find_task_function(module, task_id):
    """Find the task function for the given task ID"""
    # Look for PythonOperator tasks
    for name, obj in vars(module).items():
        if isinstance(obj, dict) and task_id in obj:
            task_obj = obj[task_id]
            if hasattr(task_obj, 'python_callable'):
                return task_obj.python_callable
    
    # Try to find function by name
    for name, obj in vars(module).items():
        if callable(obj) and name == task_id:
            return obj
    
    raise ValueError(f"Could not find task function for task ID {task_id}")

def run_task(dag_id, task_id, execution_date):
    """Run the task directly"""
    print(f"\n--- Direct execution of {dag_id}.{task_id} for {execution_date} ---\n")
    
    # Setup environment
    setup_environment()
    
    # Import the DAG module
    module = import_dag_file(dag_id)
    
    # Find the task function
    task_func = find_task_function(module, task_id)
    
    # Execute the task
    print(f"\n--- Executing task {task_id} ---")
    result = task_func()
    print(f"\n--- Task execution complete ---")
    print(f"Result: {result}")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    
    dag_id = sys.argv[1]
    task_id = sys.argv[2]
    execution_date = sys.argv[3]
    
    run_task(dag_id, task_id, execution_date) 