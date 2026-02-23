from pathlib import Path

from airflow.models import DagBag


def test_weather_dag_loaded():
    project_root = Path(__file__).resolve().parents[1]
    dag_folder = project_root / "airflow" / "dags"

    dag_bag = DagBag(
        dag_folder=str(dag_folder),
        include_examples=False
    )

    assert dag_bag.import_errors == {}
    assert "weather-orchestrator" in dag_bag.dags