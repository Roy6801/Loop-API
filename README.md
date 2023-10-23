# Store Activity Report Generation

This project is designed to generate store activity reports, calculating uptime and downtime for a given store over specific time intervals, such as the last hour, last day, and last week.

## Table of Contents

- [Introduction](#introduction)
- [Project Structure](#project-structure)
- [How It Works](#how-it-works)
- [Usage](#usage)
- [Dependencies](#dependencies)
- [Time Complexity](#time-complexity)

## Introduction

In many businesses, it's essential to monitor store activity to track uptime and downtime. This project uses Django and Celery to automate the process of generating activity reports for different stores. It calculates the time a store is operational (uptime) and the time it's not (downtime) over specific intervals.

## Project Structure

The project consists of the following key components:

1. Django Models: `Store`, `TimeZone`, `BusinessHour`, `Activity`, `Report`

   - `Store`: Represents a store entity and stores attributes like ID, timezone, local business hours, and activities.
   - `TimeZone`: Stores timezone information for each store.
   - `BusinessHour`: Stores business hours for each day of the week.
   - `Activity`: Records store activities, including timestamps and status (active or not).
   - `Report`: Keeps track of generated reports, including a unique report ID.

2. Utility Functions: `functions.py`, `store.py`, `activity_report.py`, `handler.py`

   - `functions.py`: Contains utility functions to retrieve report IDs, stores, and convert timestamps.
   - `store.py`: Defines the `Store` class to manage store-related operations.
   - `activity_report.py`: Defines the `ActivityReport` class to calculate uptime and downtime.
   - `handler.py`: Defines the `trigger_report_generation` function that triggers the generation of store activity reports for a specific time and parallelizes the process for efficiency.

3. Celery Tasks: `tasks.py`

   - Contains Celery tasks to process batches of stores, generate reports, and save report files.

4. Docker Configuration: `Dockerfile` and `docker-compose.yml`
   - The Docker configuration files are provided for containerized deployment, including the setup of the Django application, Celery workers, and Redis.

## How It Works

1. **Store Management (Store Class)**

   - The `Store` class manages store attributes, such as timezone, local business hours, and activities.
   - It sets the store's timezone and retrieves local business hours for each day of the week.
   - It retrieves a list of store activities within a specified time range.

2. **Activity Report Generation (ActivityReport Class)**

   - The `ActivityReport` class calculates uptime and downtime based on activities within specific time frames.
   - It accounts for different business hours on different days of the week.
   - It accumulates uptime and downtime for the last hour, last day, and last week.

3. **Celery Tasks**

   - Celery tasks are used to process batches of stores in parallel.
   - The `process_batch` task processes multiple stores in parallel, leveraging ThreadPoolExecutor for efficiency.
   - The `save_report_file` task saves generated reports to CSV files and updates the report status.

4. **Report Trigger Handler**
   - The `trigger_report_generation` function is a custom function used to initiate report generation.
   - It sets the current time, calculates timestamps for the last hour, last day, and last week.
   - Retrieves a list of stores with recent activities and divides them into batches for parallel processing.
   - Uses a Celery chord to execute batch processing and report file saving in parallel.

## Usage

1. Set up a Django project and configure Celery for task processing.

2. Populate the database with store data, timezones, business hours, and activities.

To run the project using Docker and Docker Compose, follow these steps:

1. Build and start the containers:
   ```bash
   docker-compose up --build
   ```
2. Access the Django application at http://localhost:8000.

3. Use the `trigger_report_generation` function to generate store activity reports for a specific time frame.

4. Monitor Celery tasks and reports using Flower, which is accessible at http://localhost:5555.

5. The Celery workers use a prefork concurrency model, with each process handling a batch of store IDs concurrently. The batch size, specified as an argument in the `process_batch` function, represents the number of threads for concurrent store ID processing with subtasks.

### Example Usage

```python
# Trigger report generation for a specific time frame
report_id = get_report_id()
trigger_report_generation(report_id, batch_size=4)

# Retrieve a report for a store
report_data = get_report(report_id)

# Retrieve the report file for a store
report_file = get_report_file(report_id)
```
