ARG AIRFLOW_VERSION
ARG PYTHON_VERSION


FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}

# Re-declare ARGs after FROM to make them available in build stages
ARG AIRFLOW_VERSION
ARG PYTHON_VERSION

# Now construct the CONSTRAINT_URL
ARG CONSTRAINT_URL="https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-${PYTHON_VERSION}.txt"

# Switch to root to install system dependencies
USER root

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Install additional Python dependencies
COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir \
    -r /requirements.txt \
    -c ${CONSTRAINT_URL}
