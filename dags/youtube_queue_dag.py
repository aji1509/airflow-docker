from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'youtube_queue_task',
    default_args=default_args,
    description='A DAG that sends a task to the youtube queue every minute',
    schedule_interval='* * * * *',  # Run every minute
    catchup=False,
)

# This task will run on workers subscribed to the 'youtube' queue
youtube_task = BashOperator(
    task_id='youtube_task',
    bash_command='echo "hello world"',
    queue='youtube',  # Assign to youtube queue
    dag=dag,
)

# Optional: Add a task that shows which worker actually executed the task
execution_info = BashOperator(
    task_id='execution_info',
    bash_command='echo "Task executed on worker: $(hostname) with IP: $(hostname -i)"',
    queue='youtube',  # Also assign to youtube queue
    dag=dag,
)

youtube_task >> execution_info 