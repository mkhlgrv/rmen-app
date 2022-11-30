import os
from dotenv import load_dotenv
load_dotenv()
import csv
from copy import copy
from datetime import datetime
import sqlite3 as sl
import numpy as np
from rmen.utils import interim_storage_path as storage_path
from rmen.utils import generate_date_series
from logger import logger

logger.info("Initializing storage: starts")

rmedb_storage_path = os.getenv("rmedb_storage")
# TODO add to R rmedb::download this code to write metadata:
# TODO write.csv(rmedb::get.variables.df(), file = "metadata.csv", row.names = FALSE)

metadata_path = os.path.join(rmedb_storage_path, "metadata.csv")

sql_path = os.path.join(os.getenv("project_dir"), "assets", "sql")

with open(os.path.join(sql_path, "drop_variable.sql")) as f:
    drop_variable = f.read()
with open(os.path.join(sql_path, "drop_value.sql")) as f:
    drop_value = f.read()
with open(os.path.join(sql_path, "drop_predictor.sql")) as f:
    drop_predictor = f.read()
    
with open(os.path.join(sql_path, "drop_publication_shift.sql")) as f:
    drop_publication_shift = f.read()
with open(os.path.join(sql_path, "drop_date_range.sql")) as f:
    drop_date_range = f.read()
    
    
with open(os.path.join(sql_path, "create_variable.sql")) as f:
    create_variable = f.read()
with open(os.path.join(sql_path, "create_value.sql")) as f:
    create_value = f.read()
with open(os.path.join(sql_path, "create_predictor.sql")) as f:
    create_predictor = f.read()



with open(os.path.join(sql_path, "delete_from_variable.sql")) as f:
    delete_from_variable = f.read()
with open(os.path.join(sql_path, "delete_from_value.sql")) as f:
    delete_from_value = f.read()


with open(os.path.join(sql_path, "insert_variable.sql")) as f:
    insert_variable = f.read()
with open(os.path.join(sql_path, "insert_value.sql")) as f:
    insert_value = f.read()

with open(os.path.join(sql_path, "create_publication_shift.sql")) as f:
    create_publication_shift = f.read()
with open(os.path.join(sql_path, "create_date_range.sql")) as f:
    create_date_range = f.read()

create_index = []
for index in ("ticker", "dt"):
    with open(os.path.join(sql_path, f"value_index_{index}.sql")) as f:
        create_index.append(f.read())

def init_storage():
    with sl.connect(storage_path) as conn:
        conn.execute('PRAGMA locking_mode = EXCLUSIVE')
        cursor = conn.cursor()
        cursor.execute(drop_variable)
        cursor.execute(create_variable)
        cursor.execute(drop_value)
        cursor.execute(create_value)
        cursor.execute(drop_predictor)
        cursor.execute(create_predictor)
        
        cursor.execute(drop_publication_shift)
        cursor.execute(drop_date_range)
        cursor.execute(create_publication_shift)
        cursor.execute(create_date_range)
        
        for query in create_index:
            cursor.execute(query)
        conn.create_function('log', 1, np.log)

        conn.commit()

def update_storage():
    with sl.connect(storage_path) as conn:

        cursor = conn.cursor()

        cursor.execute(delete_from_value)
        cursor.execute(delete_from_variable)

        with open(metadata_path, "r") as f:
            reader = csv.reader(f)
            next(reader, None)
            cursor.executemany(insert_variable, reader)
        # костыль -------------
        cursor.execute("select ticker from variable where source = 'internal' and ticker like '%mont%'")
        monthly_internal_tickers = [i for i, in cursor.fetchall()]
        # ----------------

        for i in os.listdir(os.path.join(rmedb_storage_path, "tf")):
            ticker = i[:-4]
            if ticker not in monthly_internal_tickers:

                with open(os.path.join(rmedb_storage_path, "tf", i), "r") as f:
                    reader = csv.reader(f)
                    next(reader, None)
                    writer = ((ticker
                               , datetime.strptime(dt, "%Y-%m-%d")
                               , float(value)) for dt, value, _ in reader)
                    cursor.executemany(insert_value, writer)
            else:
                actual_dt = None
                with open(os.path.join(rmedb_storage_path, "tf", i), "r") as f:
                    reader = csv.reader(f)
                    next(reader, None)
                    for dt, value, _ in reader:
                        dt_datetime = datetime.strptime(dt, "%Y-%m-%d")
                        if (actual_dt is None) or (dt_datetime.month == actual_dt.month):
                            actual_dt = datetime(dt_datetime.year, dt_datetime.month, 1)
                            actual_value = copy(value)
                        else:
                            writer = (ticker, actual_dt, actual_value)
                            cursor.execute(insert_value, writer)
                            actual_dt = datetime(dt_datetime.year, dt_datetime.month, 1)
                            actual_value = copy(value)
          
        conn.commit()                

if __name__ == "__main__":
    logger.info("Starts storage initializing")
    init_storage()
    logger.info("Storage initialized")
    logger.info("Starts storage updating")
    update_storage()
    logger.info("Storage updated")