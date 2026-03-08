import sys
from datetime import datetime

from airflow.operators.python import PythonOperator
from airflow.providers.standard.operators.empty import EmptyOperator

from airflow import DAG

sys.path.append('/opt/airflow')
from api.insert_data import main

with DAG(
    dag_id="weather-orchestrator",
    start_date=datetime(2024, 1, 1),
    schedule="@hourly",
    catchup=False,
    tags=["etl", "weather"],
) as dag:
    
    start = EmptyOperator(task_id='start')

    insert_weather_data = PythonOperator(
        task_id="insert_weather_data",
        python_callable=main,
    )

    end = EmptyOperator(task_id='end')

    start >> insert_weather_data >> end