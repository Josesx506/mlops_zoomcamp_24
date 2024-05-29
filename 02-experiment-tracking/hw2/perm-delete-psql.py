import os
import sys

import psycopg2

sys.path.insert(0, os.getcwd())

from env import DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


def perm_delete_exp():
    connection = psycopg2.connect(database=DB_NAME, 
                                  user=DB_USER, 
                                  password=DB_PASSWORD, 
                                  host="localhost", 
                                  port=int(DB_PORT))
    
    with connection.cursor() as cursor:
        queries = """
            DELETE FROM experiment_tags WHERE experiment_id=ANY(SELECT experiment_id FROM experiments where lifecycle_stage='deleted');
            DELETE FROM latest_metrics WHERE run_uuid=ANY(SELECT run_uuid FROM runs WHERE experiment_id=ANY(SELECT experiment_id FROM experiments where lifecycle_stage='deleted'));
            DELETE FROM metrics WHERE run_uuid=ANY(SELECT run_uuid FROM runs WHERE experiment_id=ANY(SELECT experiment_id FROM experiments where lifecycle_stage='deleted'));
            DELETE FROM tags WHERE run_uuid=ANY(SELECT run_uuid FROM runs WHERE experiment_id=ANY(SELECT experiment_id FROM experiments where lifecycle_stage='deleted'));
            DELETE FROM params WHERE run_uuid=ANY(SELECT run_uuid FROM runs where experiment_id=ANY(SELECT experiment_id FROM experiments where lifecycle_stage='deleted'));
            DELETE FROM runs WHERE experiment_id=ANY(SELECT experiment_id FROM experiments where lifecycle_stage='deleted');
            DELETE FROM datasets WHERE experiment_id=ANY(SELECT experiment_id FROM experiments where lifecycle_stage='deleted');
            DELETE FROM experiments where lifecycle_stage='deleted';
        """
        for query in queries.splitlines()[1:-1]:
            cursor.execute(query.strip())
    connection.commit()
    connection.close()


if __name__ == "__main__":
    perm_delete_exp()