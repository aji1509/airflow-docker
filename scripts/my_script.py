#!/usr/bin/env python
import time
import platform
import os

# This is a simple test script that prints some information
print("Script execution started!")
print(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Running on: {platform.node()}")
print(f"Python version: {platform.python_version()}")
print(f"Current working directory: {os.getcwd()}")

# Simulate some work
print("Performing calculation...")
result = sum(i for i in range(1000000))
print(f"Calculation result: {result}")

print("Script execution completed successfully!")
