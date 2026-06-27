from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime
from pendulum import timezone

with DAG(
    dag_id='stock_analyzer_us_1',
    start_date=datetime(2024, 1, 1, tzinfo=timezone('America/New_York')),
    schedule='0 19 1,15 * *',
    catchup=False,
    tags=['stock_analyzer_us_1'],
) as dag:

    # Task 1
    co_fetcher = DockerOperator(
        task_id='co_fetcher',
        image='stock-analyzer-us:v2.0',
        command='python -m us.data_pipeline.company_symbols.us_co_symbol_fetcher',
        mount_tmp_dir=False,   # ← 必加
        docker_url='unix://var/run/docker.sock',
        auto_remove='success',
        network_mode='airflow_workspace_airflow-network',
    )

    # Task 2
    co_fund_fetcher = DockerOperator(
        task_id='co_fund_fetcher',
        image='stock-analyzer-us:v2.0',
        command='python -m us.data_pipeline.company_fundamentals.us_co_fundamentals_fetcher',
        mount_tmp_dir=False,   # ← 必加
        docker_url='unix://var/run/docker.sock',
        auto_remove='success',
        network_mode='airflow_workspace_airflow-network',
    )

    # Task 3
    co_screener = DockerOperator(
        task_id='co_screener',
        image='stock-analyzer-us:v2.0',
        command='python -m us.data_pipeline.company_screening.us_co_screener',
        mount_tmp_dir=False,   # ← 必加
        docker_url='unix://var/run/docker.sock',
        auto_remove='success',
        network_mode='airflow_workspace_airflow-network',
    )

    co_fetcher >> co_fund_fetcher >> co_screener