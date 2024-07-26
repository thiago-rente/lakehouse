import os
import json
import requests
from bs4 import BeautifulSoup
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.mongo.hooks.mongo import MongoHook
import pandas as pd

from datetime import datetime,timedelta

def on_failure_callback(**context):
    print(f"Task {context['task_instance_key_str']} failed.")

def get_games(year, page):
    url = f"https://opencritic.com/browse/all/{year}?page={page}"
    print(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    games_found = soup.find_all("div", class_="row no-gutters py-2 game-row align-items-center")
    
    return games_found

def scrape_opencritic():
    year = datetime.now().year
    print(year)
    p = 1
    games = get_games(year, p)

    df_games = []

    for game in games:
        df_games.append([{"score": game.find("div", class_="score col-auto").text.strip(),
                        "name": game.find("div", class_="game-name col").text.strip(),
                        "platforms": game.find("div", class_="platforms col-auto").text.strip(),
                        "release_date": game.find("div", class_="first-release-date col-auto").text.strip()
                        }])

    while(str(games) != '[]'):
        p = p + 1
        games = get_games(year, p)

        if(games != '[]'):
            for game in games:
                df_games.append([{"score": game.find("div", class_="score col-auto").text.strip(),
                                "name": game.find("div", class_="game-name col").text.strip(),
                                "platforms": game.find("div", class_="platforms col-auto").text.strip(),
                                "release_date": game.find("div", class_="first-release-date col-auto").text.strip()
                                }])

    print(df_games)

    return df_games

def upload_games_mongo(ti, **context):

    print(context["games"])
    games = context["games"]

    games_dict = {"date": str(datetime.now()), "list": games}
    print(games_dict)

    try:
        hook = MongoHook(conn_id='opencritic_database_connection')
        client = hook.get_conn()
        games = client.opencritic['games']
        
        print(f"Connected to MongoDB - {client.server_info()}")

        #print(f"Databases: {client.list_database_names()}")
        #print(games.find({"name": "Final Fantasy VII Rebirth"})[0])

        games.insert_one(games_dict)
        
    except Exception as e:
        print(f"Error connecting to MongoDB -- {e}")

with DAG(
    dag_id="dag_opencritic_database",
    schedule_interval=None,
    catchup=False,
    tags=["opencritic", "database", "mongodb"],
    default_args={
        "retries": 0,
        "retry_delay": timedelta(minutes=5),
        'on_failure_callback': on_failure_callback
    }
) as dag:
    
    task_scrape_opencritic = PythonOperator(
        task_id="task_scrape_opencritic",
        python_callable=scrape_opencritic,
        do_xcom_push=True,
        dag=dag,
    )

    upload_mongodb = PythonOperator(
        task_id='upload_mongodb',
        python_callable=upload_games_mongo,
        op_kwargs={ "games": task_scrape_opencritic.output },
        dag=dag
        )

    task_scrape_opencritic >> upload_mongodb
