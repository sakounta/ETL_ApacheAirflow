import os
from pathlib import Path
import pandas as pd
from datetime import datetime
from airflow.utils.dates import days_ago
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.models import Variable
from airflow.utils.task_group import TaskGroup
from airflow.utils.edgemodifier import Label

# Definition of relative paths

FILE_PATH = (Path(__file__).parent.parent / "datasets" / "bank_transactions_data_2.csv").resolve()
OUTPUT_PATH = (Path(__file__).parent.parent / "output" / "{0}.csv").resolve()

default_args = {
    'owner': 'kounta'
}

# Function for reading the CSV file
def read_csv_file(ti):
    df = pd.read_csv(FILE_PATH)

    print(df.head())  

    ti.xcom_push(key='my_csv', value=df.to_json())

# Function for deleting zero values
def remove_null_values(ti):
    json_data = ti.xcom_pull(key='my_csv')
    df = pd.read_json(json_data)
    
    df = df.dropna()

    print(df.head())

    ti.xcom_push(key='my_clean_csv', value=df.to_json())

# Determining the branch according to the Airflow variable
def determine_branch():
    transform_action = Variable.get("transform_action", default_var=None)
    
    print(f"Branching action: {transform_action}")

    if transform_action.startswith('filter'):
        return f"filtering.{transform_action}"
    elif transform_action == 'groupby_transaction_type':
        return "grouping.groupby_transaction_type"

# Filter by location 
def filter_by_location(ti, location):
    json_data = ti.xcom_pull(key='my_clean_csv')
    df = pd.read_json(json_data)

    if 'Location' not in df.columns:
        print("Erreur: La colonne 'Location' n'existe pas dans le dataset.")
        return

    location_df = df[df['Location'] == location]
    
    location_df.to_csv(str(OUTPUT_PATH).format('filter_by_location'), index=False)

# Filter by group transaction type
def groupby_transaction_type(ti):
    json_data = ti.xcom_pull(key='my_clean_csv')
    df = pd.read_json(json_data)

    if 'TransactionType' not in df.columns:
        print("Erreur: La colonne 'TransactionType' n'existe pas dans le dataset.")
        return

    grouped_df = df.groupby('TransactionType').agg({
        'CustomerAge': 'mean',
        'TransactionAmount': 'sum'
    }).reset_index()

    grouped_df.to_csv(str(OUTPUT_PATH).format('grouped_by_account_type'), index=False)

# Définition of DAG
with DAG(
    dag_id='transaction_processing_pipeline',
    description='Pipeline Airflow pour filtrer et grouper les transactions bancaires',
    default_args=default_args,
    start_date=days_ago(1),
    schedule_interval='@once',
    tags=['banking', 'transactions', 'airflow']
) as dag:
    
    with TaskGroup('reading_and_preprocessing') as reading_and_preprocessing:
        read_csv_file = PythonOperator(
            task_id='read_csv_file',
            python_callable=read_csv_file
        )

        remove_null_values = PythonOperator(
            task_id='remove_null_values',
            python_callable=remove_null_values
        )

        read_csv_file >> remove_null_values

    determine_branch = BranchPythonOperator(
        task_id='determine_branch',
        python_callable=determine_branch
    )
    
    with TaskGroup('filtering') as filtering:
        filter_by_location = PythonOperator(
            task_id='filter_by_location',
            python_callable=filter_by_location,
            op_kwargs={'location': 'San Diego'}
        )


    with TaskGroup('grouping') as grouping:
        groupby_transaction_type = PythonOperator(
            task_id='groupby_transaction_type',
            python_callable=groupby_transaction_type
        )
    
    # Definition of the Taskflow
    reading_and_preprocessing >> Label('preprocessed data') >> determine_branch >> Label('branch on condition') >> [filtering, grouping]
