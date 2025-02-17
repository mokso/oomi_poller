CREATE OR REPLACE VIEW energy_cost AS
    SELECT 
        c.time,
        c.value as consumption,
        p.value as production,
        s.buy_price,
        s.sell_price,
        s.buy_price * c.value as buy_cost,
        s.sell_price * p.value as sell_income,
        s.buy_price * c.value - s.sell_price * p.value as totalcost

    FROM energy_consumption c
        JOIN energy_production p ON c.time = p.time
        JOIN energy_spot_price s ON c.time = s.time