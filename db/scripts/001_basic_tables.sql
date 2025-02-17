CREATE TABLE energy_consumption (
    "time" TIMESTAMPTZ NOT NULL PRIMARY KEY,
    value DOUBLE PRECISION NOT NULL
);

CREATE TABLE energy_production (
    "time" TIMESTAMPTZ PRIMARY KEY,
    value DOUBLE PRECISION NOT NULL
);

-- Energy consumption marginal
CREATE TABLE energy_consumption_marginal (
    id SERIAL PRIMARY KEY,
    valid_from TIMESTAMPTZ  NOT NULL UNIQUE,
    value REAL NOT NULL DEFAULT 0
);

-- insert  marginal value
INSERT INTO energy_consumption_marginal (valid_from, value) VALUES ('2000-01-01Z', 0.0025);
INSERT INTO energy_consumption_marginal (valid_from, value) VALUES ('2024-03-01Z', 0.0059);

--Energy production marginal
CREATE TABLE energy_production_marginal (
    id SERIAL PRIMARY KEY,
    valid_from TIMESTAMPTZ NOT NULL UNIQUE,
    value REAL NOT NULL DEFAULT 0
);

INSERT INTO energy_production_marginal (valid_from, value)  VALUES ('2000-01-01Z', 0);

-- Energy spot price
CREATE TABLE energy_spot_price (
    "time" TIMESTAMPTZ PRIMARY KEY,
    price REAL, -- the actual SPOT price
    buy_price REAL, -- price + energy_consumption_marginal
    sell_price REAL -- price - energy_production_marginal
);
