CREATE TABLE PREDICTOR (
     ticker TEXT NOT NULL
    , lag INT NOT NULL
    , FOREIGN KEY (ticker)
    REFERENCES VARIABLE (ticker)
);