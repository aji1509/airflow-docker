from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import socket

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'worker_specific_tasks',
    default_args=default_args,
    description='A DAG that sends tasks to specific workers',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

# This task will run on any available worker (default queue)
default_task = BashOperator(
    task_id='default_queue_task',
    bash_command='echo "Running on worker: $(hostname) with IP: $(hostname -i)"',
    dag=dag,
)

# This task will run only on worker1
worker1_task = BashOperator(
    task_id='worker1_task',
    bash_command='echo "Running on worker1: $(hostname) with IP: $(hostname -i)"',
    queue='worker1',  # Specific queue for worker1
    dag=dag,
)

# This task will run only on worker2
worker2_task = BashOperator(
    task_id='worker2_task',
    bash_command='echo "Running on worker2: $(hostname) with IP: $(hostname -i)"',
    queue='worker2',  # Specific queue for worker2
    dag=dag,
)

# This function will report which worker the task is running on
def get_worker_info():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return f"Task running on worker with hostname: {hostname} and IP: {ip}"

# This task will run on any available worker (default queue)
python_task = PythonOperator(
    task_id='python_task',
    python_callable=get_worker_info,
    dag=dag,
)

default_task >> [worker1_task, worker2_task] >> python_task 