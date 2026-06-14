from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime
from pendulum import timezone

with DAG(
    dag_id='stock_analyzer_us_2',
    start_date=datetime(2024, 1, 1, tzinfo=timezone('America/New_York')),
    schedule='0 18 * * 1-5',
    catchup=False,
    tags=['stock_analyzer_us_2'],
) as dag:

    # Task 1
    fetcher = DockerOperator(
        task_id='fetcher',
        image='stock-analyzer-us:v1.0',
        command='python -m us.data_pipeline.company_history_prices.history_price_fetcher',
        mount_tmp_dir=False,   # ← 必加
        docker_url='unix://var/run/docker.sock',
        auto_remove='success',
        network_mode='airflow_workspace_airflow-network',
    )

    # Task 2
    cleaner = DockerOperator(
        task_id='cleaner',
        image='stock-analyzer-us:v1.0',
        command='python -m us.data_pipeline.company_history_prices.history_price_cleaner',
        mount_tmp_dir=False,   # ← 必加
        docker_url='unix://var/run/docker.sock',
        auto_remove='success',
        network_mode='airflow_workspace_airflow-network',
    )

    # Task 3
    calculator = DockerOperator(
        task_id='calculator',
        image='stock-analyzer-us:v1.0',
        command='python -m us.data_pipeline.company_history_prices.history_price_calculator',
        mount_tmp_dir=False,   # ← 必加
        docker_url='unix://var/run/docker.sock',
        auto_remove='success',
        network_mode='airflow_workspace_airflow-network',
    )
    # Task 4
    unioner = DockerOperator(
        task_id='unioner',
        image='stock-analyzer-us:v1.0',
        command='python -m us.data_pipeline.company_history_prices.history_price_union',
        mount_tmp_dir=False,   # ← 必加
        docker_url='unix://var/run/docker.sock',
        auto_remove='success',
        network_mode='airflow_workspace_airflow-network',
    )

    # Task 5
    conclusion = DockerOperator(
        task_id='entry_conclusion',
        image='stock-analyzer-us:v1.0',
        command='dbt run --project-dir /app/stock_analyzer_us/us/dbt_project --profiles-dir /app/stock_analyzer_us/us/dbt_project --select +entry_conclusion',
        mount_tmp_dir=False,   # ← 必加
        docker_url='unix://var/run/docker.sock',
        auto_remove='success',
        network_mode='airflow_workspace_airflow-network',
    )

    # Task 6
    upload_sheet = DockerOperator(
        task_id='upload_sheet',
        image='stock-analyzer-us:v1.0',
        command='python -m us.upload_pipeline.upload_sheet',
        mount_tmp_dir=False,   # ← 必加
        docker_url='unix://var/run/docker.sock',
        auto_remove='success',
        network_mode='airflow_workspace_airflow-network',
    )

    # Task 7
    upload_snowflake = DockerOperator(
        task_id='upload_snowflake',
        image='stock-analyzer-us:v1.0',
        command='python -m us.upload_pipeline.minio_to_snowflake',
        mount_tmp_dir=False,   # ← 必加
        docker_url='unix://var/run/docker.sock',
        auto_remove='success',
        network_mode='airflow_workspace_airflow-network',
    )

    fetcher >> cleaner >> calculator
    calculator >> [unioner, upload_snowflake]
    unioner >> conclusion >> upload_sheet