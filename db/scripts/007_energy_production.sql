CREATE TABLE IF NOT EXISTS energy_solar_generation (
    datetime TIMESTAMPTZ PRIMARY KEY,
    min_power_kw FLOAT,
    max_power_kw FLOAT,
    mean_power_kw FLOAT,
    hourly_generation_kwh FLOAT
);

INSERT INTO energy_solar_generation (datetime, min_power_kw, max_power_kw, mean_power_kw, hourly_generation_kwh)
VALUES ('2023-06-01 00:00:00', 0.0, 0.0, 0.0, 0.0);