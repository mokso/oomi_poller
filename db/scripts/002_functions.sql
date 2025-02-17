


-- Trigger function to update buy_price and sell_price
CREATE OR REPLACE FUNCTION update_energy_spot_price()
RETURNS TRIGGER AS $$
BEGIN
    -- Update buy_price based on the latest energy_consumption_marginal value
    NEW.buy_price = NEW.price + (
        SELECT value
        FROM energy_consumption_marginal
        ORDER BY valid_from DESC
        LIMIT 1
    );

    -- Update sell_price based on the latest energy_production_marginal value
    NEW.sell_price = NEW.price - (
        SELECT value
        FROM energy_production_marginal
        ORDER BY valid_from DESC
        LIMIT 1
    );

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER before_insert_energy_spot_price
BEFORE INSERT ON energy_spot_price
FOR EACH ROW
EXECUTE FUNCTION update_energy_spot_price();
