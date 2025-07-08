SHOW databases;
USE project_PM;
CREATE TABLE basic_data (
    year INT,
    month INT,
    day INT,
    hour INT,
    district VARCHAR(100),
    datetime DATETIME,
    total_population INT,
    season VARCHAR(20),
    commute_time VARCHAR(20),
    weekend_flag BOOLEAN,
    precipitation FLOAT,
    temperature FLOAT,
    humidity FLOAT,
    wind_speed FLOAT
);
SHOW tables;
SELECT  FROM basic_data where year>2024;
DROP Tables basic_data;
CREATE TABLE basic_data (
    year INT,
    month INT,
    day INT,
    hour INT,
    district VARCHAR(100),
    datetime DATETIME,
    total_population INT,
    season VARCHAR(20),
    commute_time VARCHAR(20),
    weekend_flag BOOLEAN,
    precipitation FLOAT,
    temperature FLOAT,
    humidity FLOAT,
    wind_speed FLOAT
);
ALTER TABLE basic_data ADD COLUMN rental_count INT;

SELECT * FROM basic_data where year = 2025 && month=5;
