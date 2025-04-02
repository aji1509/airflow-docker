# Apache Airflow Docker Setup

This repository contains Docker configuration for setting up Apache Airflow with CeleryExecutor for distributed task processing. The setup includes a master node and worker nodes configuration.

## Features

- Uses CeleryExecutor with Redis and PostgreSQL
- Scalable architecture with separate master and worker nodes
- Works on M1 Mac
- Includes Superset, Minio, and other useful services

## Prerequisites

- Docker and Docker Compose
- Git
- Basic understanding of Airflow concepts

## Directory Structure

The setup uses several directories that are mounted into the containers:

- `dags/`: Place your Airflow DAG files here
- `logs/`: Airflow logs will be stored here
- `plugins/`: Custom Airflow plugins
- `scripts/`: Custom scripts for Airflow tasks
- `sql/`: SQL files for database operations
- `data/`: Data directory for MinIO storage
- `pg-init-scripts/`: Initialization scripts for PostgreSQL

These directories are mounted in both the master and worker containers to ensure consistency across the cluster.

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```
AIRFLOW_UID=50000
AIRFLOW_VERSION=2.7.3
PYTHON_VERSION=3.10
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
AIRFLOW_WWW_USER_USERNAME=airflow
AIRFLOW_WWW_USER_PASSWORD=airflow
```

## Master Node Setup

### 1. Prepare Directory Structure

```bash
mkdir -p dags logs plugins scripts data pg-init-scripts sql
```

### 2. Build and Start the Master Node

```bash
# Start the Airflow master node
docker-compose -f docker-compose.yaml up -d
```

This will initialize the database, create the admin user, and start all required services:
- PostgreSQL
- Redis
- Airflow Webserver
- Airflow Scheduler
- Airflow Triggerer

### 3. Access Airflow UI

The Airflow UI will be available at: `http://localhost:8080`

Default credentials are:
- Username: airflow
- Password: airflow

## Worker Node Setup

To set up worker nodes that connect to your existing master node:

### 1. Copy Required Files to Worker Machine

On each worker machine, copy the following files:
- `worker.dockerfile`
- `worker-compose.yaml`
- `requirements.txt`

### 2. Update Worker Configuration

Edit the `worker.dockerfile` to point to your master node:

```dockerfile
# Set environment variables to connect to the master node
ENV AIRFLOW__CORE__EXECUTOR=CeleryExecutor \
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@YOUR_MASTER_IP:5433/airflow \
    AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@YOUR_MASTER_IP:5433/airflow \
    AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:airflow@YOUR_MASTER_IP:5433/airflow \
    AIRFLOW__CELERY__BROKER_URL=redis://:@YOUR_MASTER_IP:6379/0
```

Replace `YOUR_MASTER_IP` with the actual IP address of your master node (e.g., 172.29.25.15).

### 3. Build and Start the Worker

```bash
# Build the worker
docker-compose -f worker-compose.yaml build

# Start the worker
docker-compose -f worker-compose.yaml up -d
```

The worker will automatically register itself with the master node. You can view connected workers in the Airflow UI under Admin > Clusters.

### 4. Directing Tasks to Specific Workers

To send tasks to specific workers, use the queue system:

1. Configure workers to listen to specific queues:

   ```yaml
   # In worker-compose.yaml
   services:
     airflow-worker1:
       # ... other settings ...
       environment:
         # ... other environment variables ...
         AIRFLOW__CELERY__CELERY_QUEUES: 'default,worker1'
       command: celery worker -q default,worker1
     
     airflow-worker2:
       # ... other settings ...
       environment:
         # ... other environment variables ...
         AIRFLOW__CELERY__CELERY_QUEUES: 'default,worker2'
       command: celery worker -q default,worker2
   ```

2. In your DAG files, assign tasks to specific queues:

   ```python
   # Task that will run on any worker (default queue)
   default_task = BashOperator(
       task_id='default_task',
       bash_command='echo "Running on default queue"',
       dag=dag,
   )
   
   # Task that will run only on worker1
   worker1_task = BashOperator(
       task_id='worker1_task',
       bash_command='echo "Running on worker1"',
       queue='worker1',
       dag=dag,
   )
   
   # Task that will run only on worker2
   worker2_task = BashOperator(
       task_id='worker2_task',
       bash_command='echo "Running on worker2"',
       queue='worker2',
       dag=dag,
   )
   ```

With this setup:
- Tasks assigned to the 'default' queue will run on any available worker
- Tasks assigned to the 'worker1' queue will only run on airflow-worker1
- Tasks assigned to the 'worker2' queue will only run on airflow-worker2

### 5. Checking Worker Status

You can check which workers are active and what queues they're subscribed to in the Airflow UI:
1. Go to Admin → Clusters
2. Check the "Queues" column to see which queues each worker is processing

## Troubleshooting

### Common Issues

1. **Database Connection Issues**: Ensure PostgreSQL is accessible from worker nodes on port 5433

2. **Redis Connection Issues**: Ensure Redis is accessible from worker nodes on port 6379

3. **Package Conflicts**: If you encounter dependency conflicts, update your requirements.txt. Note that apache-airflow-providers-redis 3.4.1 conflicts with redis==4.5.5, use redis==4.5.4 instead.

4. **Hostname Display Issues**: The worker config uses IP address as hostname by default. If you need to customize it, edit the `AIRFLOW__CORE__HOSTNAME_CALLABLE` in worker-compose.yaml.

## Stopping the Services

### Master Node
```bash
docker-compose -f docker-compose.yaml down
```

### Worker Node
```bash
docker-compose -f worker-compose.yaml down
```

## Additional Services

- **Flower**: Celery monitoring tool available at `http://localhost:5555`
- **Superset**: Data exploration and visualization at `http://localhost:8091`
- **MinIO**: Object storage service at `http://localhost:9001` (Console) and `http://localhost:9000` (API)