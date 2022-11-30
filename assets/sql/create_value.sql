CREATE TABLE VALUE (
                       ticker TEXT NOT NULL
    , dt TEXT NOT NULL
    , value REAL NOT NULL
    , FOREIGN KEY (ticker)
                           REFERENCES VARIABLE (ticker)
);