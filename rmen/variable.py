from dotenv import load_dotenv
load_dotenv()
from typing import Optional
import sqlite3 as sl
from rmen.utils import interim_storage_path as storage_path

class Variable:
    def __init__(self
                 , ticker:str
                 , desc: Optional[str] = None
                 ):
        self.ticker = ticker
        self.desc = desc

        self.get_attributes()
        self.get_start_dt()
    def get_attributes(self):
        self.name = {}
        with sl.connect(storage_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"""SELECT 
                                source,
                                freq,
                                transform, 
                                deseason, 
                                aggregate, 
                                name_rus_tf, 
                                name_rus,
                                name_eng 
                            FROM 
                                variable 
                            WHERE 
                                ticker = '{self.ticker}'""")
            self.source, \
            self.freq, \
            self.transform, \
            self.deseason, \
            self.aggregate,\
            self.name["rus"],\
            self.name["rus_full"],\
            self.name["eng_full"] = cursor.fetchone()

    def get_start_dt(self):
        with sl.connect(storage_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT min(dt) FROM VALUE WHERE ticker = '{self.ticker}'")
            self.start_dt,  = cursor.fetchone()