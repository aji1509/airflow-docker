ARG AIRFLOW_VERSION=2.7.3
ARG PYTHON_VERSION=3.10

FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

USER root

# Install additional system packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        netcat-openbsd \
        build-essential \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Fix permissions and create necessary directories
RUN mkdir -p /opt/airflow/logs /opt/airflow/dags /opt/airflow/plugins /opt/airflow/scripts \
    && chown -R airflow:root /opt/airflow \
    && chmod -R g+w /opt/airflow

# Switch back to airflow user for better security
USER airflow

# Install additional Python packages if needed (copy requirements from the master)
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

# Set environment variables to connect to the master node
ENV AIRFLOW__CORE__EXECUTOR=CeleryExecutor \
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@172.29.25.15:5433/airflow \
    AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@172.29.25.15:5433/airflow \
    AIRFLOW__CELERY__RESULT_BACKEND=db+postgresql://airflow:airflow@172.29.25.15:5433/airflow \
    AIRFLOW__CELERY__BROKER_URL=redis://:@172.29.25.15:6379/0 \
    AIRFLOW__CORE__FERNET_KEY=81HqDtbqAywKSOumSha3BhWNOdQ26slT6K0YaZeZyPs= \
    AIRFLOW__CORE__LOAD_EXAMPLES=false \
    AIRFLOW__DATABASE__SQL_ALCHEMY_POOL_SIZE=10 \
    AIRFLOW__DATABASE__SQL_ALCHEMY_POOL_RECYCLE=1800 \
    AIRFLOW__DATABASE__SQL_ALCHEMY_MAX_OVERFLOW=5 \
    AIRFLOW__DATABASE__SQL_ALCHEMY_POOL_TIMEOUT=30 \
    AIRFLOW__DATABASE__SQL_ALCHEMY_RETRY_LIMIT=10 \
    AIRFLOW__DATABASE__SQL_ALCHEMY_RETRY_DELAY=5 \
    AIRFLOW__WEBSERVER__BASE_URL=http://172.29.25.15:8080 \
    AIRFLOW__LOGGING__REMOTE_LOGGING=false \
    AIRFLOW__LOGGING__REMOTE_BASE_LOG_FOLDER=/opt/airflow/logs

# Command to start the Celery worker
CMD ["airflow", "celery", "worker"] 