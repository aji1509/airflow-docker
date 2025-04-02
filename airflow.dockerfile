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
RUN mkdir -p /sources/logs /sources/dags /sources/plugins \
    && mkdir -p /opt/airflow/logs /opt/airflow/dags /opt/airflow/plugins \
    && chown -R airflow:root /sources /opt/airflow \
    && chmod -R g+w /sources /opt/airflow

# Switch back to airflow user for better security
USER airflow

# Install additional Python packages
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

