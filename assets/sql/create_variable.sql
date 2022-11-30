CREATE TABLE VARIABLE (
                  ticker TEXT NOT NULL PRIMARY KEY
                , source TEXT NOT NULL
                , freq TEXT NOT NULL
                , name_eng TEXT NOT NULL
                , name_rus TEXT NOT NULL
                , observation_start TEXT NOT NULL
                , use_archive BOOL NOT NULL
                , name_rus_short TEXT NOT NULL
                , transform TEXT NOT NULL
                , deseason TEXT NOT NULL
                , aggregate TEXT NOT NULL
                , internal_calc BOOL NOT NULL
                , name_rus_tf TEXT NOT NULL
);