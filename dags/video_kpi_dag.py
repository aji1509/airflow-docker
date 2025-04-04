from datetime import datetime, timedelta
import os
import subprocess
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
}

with DAG(
    'video_kpi_processor',
    default_args=default_args,
    description='A DAG to process video KPIs',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    # Define Python functions for our tasks
    def log_environment():
        """Log environment variables and directory contents for debugging"""
        # Log user and location
        print(f"Running as user: {os.getuid()}:{os.getgid()}")
        print(f"Current directory: {os.getcwd()}")
        
        # Check if script directory exists
        script_path = "/opt/airflow/scripts/til-video-kpi/worker-scripts/video-kpi"
        print(f"Script directory exists: {os.path.exists(script_path)}")
        
        # List directory contents if it exists
        if os.path.exists(script_path):
            print(f"Directory contents: {os.listdir(script_path)}")
        
        # Output Python version
        try:
            result = subprocess.run(["python", "--version"], capture_output=True, text=True)
            print(f"Python version: {result.stdout}")
        except Exception as e:
            print(f"Error getting Python version: {e}")
            
        # Test imports
        try:
            import airflow
            print(f"Airflow imported successfully: {airflow.__version__}")
        except ImportError as e:
            print(f"Failed to import airflow: {e}")
            
        return "Environment check completed"

    def run_video_kpi_script():
        """Run the video KPI script with proper error handling"""
        script_path = "/opt/airflow/scripts/til-video-kpi/worker-scripts/video-kpi/main.py"
        
        print(f"Attempting to run script: {script_path}")
        try:
            # Direct script execution instead of subprocess
            import sys
            import importlib.util
            
            # Add the script's directory to the path
            script_dir = os.path.dirname(script_path)
            if script_dir not in sys.path:
                sys.path.insert(0, script_dir)
                
            # Try to execute the script
            spec = importlib.util.spec_from_file_location("main", script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            return "Script execution completed successfully"
        except Exception as e:
            print(f"Error executing script: {e}")
            
            # Fallback to subprocess if direct import fails
            try:
                result = subprocess.run(
                    ["python", script_path], 
                    capture_output=True, 
                    text=True
                )
                
                # Log output
                print(f"Script STDOUT: {result.stdout}")
                if result.stderr:
                    print(f"Script STDERR: {result.stderr}")
                    
                # Check return code
                if result.returncode != 0:
                    raise Exception(f"Script failed with return code {result.returncode}")
                    
                return "Script execution completed successfully (subprocess)"
            except Exception as sub_e:
                print(f"Subprocess execution also failed: {sub_e}")
                raise

    # Create PythonOperator tasks
    env_task = PythonOperator(
        task_id='log_environment',
        python_callable=log_environment,
        queue='youtube',
        dag=dag,
    )

    kpi_task = PythonOperator(
        task_id='run_video_kpi_script',
        python_callable=run_video_kpi_script,
        queue='youtube',
        dag=dag,
    )

    # Task dependencies
    env_task >> kpi_task

    # You can add more tasks and dependencies as needed
    kpi_task 