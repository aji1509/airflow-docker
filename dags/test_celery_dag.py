"""
Test DAG to diagnose Celery worker issues
This is a minimal DAG that should work on any properly configured Celery worker
"""
from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
}

# Create a very simple DAG for testing
with DAG(
    'test_celery_worker',
    default_args=default_args,
    description='Simple test DAG for Celery worker',
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    # Simple Python function
    def simple_test():
        """Test function that just prints basic info"""
        print("Test function executing")
        print(f"Current working directory: {os.getcwd()}")
        print(f"User: {os.getuid()}:{os.getgid()}")
        
        # Print environment variables
        airflow_vars = {k: v for k, v in os.environ.items() if 'AIRFLOW' in k}
        print(f"Airflow environment variables: {airflow_vars}")
        
        return "Success from simple test"

    # Task 1: Echo command (Bash)
    echo_task = BashOperator(
        task_id='simple_echo',
        bash_command='echo "Hello from Celery worker" && date && hostname',
        queue='youtube',
        dag=dag,
    )
    
    # Task 2: Simple Python task
    python_task = PythonOperator(
        task_id='simple_python',
        python_callable=simple_test,
        queue='youtube',
        dag=dag,
    )
    
    # Run in sequence
    echo_task >> python_task 