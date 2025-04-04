#!/bin/bash
# Debug script for Airflow Celery worker issues
# Run this manually inside your worker container

echo "===== Airflow Worker Debug Info ====="
echo ""

echo "System Information:"
echo "-------------------------"
echo "Hostname: $(hostname)"
echo "User: $(id)"
echo "Date: $(date)"
echo "Python: $(python --version)"
echo ""

echo "Directory Information:"
echo "-------------------------"
echo "Current directory: $(pwd)"
echo "Airflow home: $AIRFLOW_HOME"
echo ""

echo "Checking critical paths:"
echo "-------------------------"
echo "Dags directory: $(ls -la /opt/airflow/dags)"
echo ""
echo "Scripts directory: $(ls -la /opt/airflow/scripts)"
echo ""

if [ -d "/opt/airflow/scripts/til-video-kpi" ]; then
    echo "til-video-kpi directory exists"
    echo "Contents: $(ls -la /opt/airflow/scripts/til-video-kpi)"
    
    if [ -d "/opt/airflow/scripts/til-video-kpi/worker-scripts/video-kpi" ]; then
        echo "video-kpi directory exists"
        echo "Contents: $(ls -la /opt/airflow/scripts/til-video-kpi/worker-scripts/video-kpi)"
        
        if [ -f "/opt/airflow/scripts/til-video-kpi/worker-scripts/video-kpi/main.py" ]; then
            echo "main.py exists"
            echo "File permissions: $(stat -c '%A %U:%G' /opt/airflow/scripts/til-video-kpi/worker-scripts/video-kpi/main.py)"
        else
            echo "ERROR: main.py does not exist!"
        fi
    else
        echo "ERROR: video-kpi directory does not exist!"
    fi
else
    echo "ERROR: til-video-kpi directory does not exist!"
fi
echo ""

echo "Environment Variables:"
echo "-------------------------"
env | grep -E "AIRFLOW|CELERY|PYTHON" | sort
echo ""

echo "Testing Celery Connection:"
echo "-------------------------"
celery --app airflow.executors.celery_executor.app inspect ping
echo ""

echo "Testing Simple Python Import:"
echo "-------------------------"
python -c "import airflow; print('Airflow imported successfully')"
echo ""

echo "Testing Direct Script Execution:"
echo "-------------------------"
if [ -f "/opt/airflow/scripts/til-video-kpi/worker-scripts/video-kpi/main.py" ]; then
    echo "Trying to run the script directly..."
    cd /opt/airflow
    python /opt/airflow/scripts/til-video-kpi/worker-scripts/video-kpi/main.py
else
    echo "Cannot test script execution as the file doesn't exist"
fi

echo "===== Debug Complete =====" 