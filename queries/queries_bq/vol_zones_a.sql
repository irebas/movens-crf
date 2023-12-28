WITH t0 AS (
	SELECT
		i1.product_id,
		i1.L1_SECTOR_ID
	FROM `pric-labo.pricing_app.input_base` i1
	LEFT JOIN `pric-labo.pricing_app.input_price_reports` i2 ON i1.product_id = i2.product_id
	WHERE i2.product_id IS NOT NULL AND i1.final_role IS NOT NULL
	AND i1.final_role NOT IN ('Fixed Prices', 'In-out/ Seasonal', 'Out of project')
),

t1 AS (
	SELECT
		t.*,
		t0.L1_SECTOR_ID AS L1,
		i5.price_zone
	FROM `pric-labo.pricing_app.input_volume` t LEFT JOIN t0 ON t.product_id = t0.product_id
	LEFT JOIN `pric-labo.pricing_app.input_price_zone_a` i5 ON t.shop_id = i5.shop_id AND t0.L1_SECTOR_ID = i5.dept
	WHERE t.shop_id IN (SELECT shop_id FROM `pric-labo.pricing_app.input_price_zone_a`) AND
	t.product_id IN (SELECT product_id FROM t0)
)

SELECT
	product_id,
	SUM(IF(price_zone=1,volume,0)) AS vol_zone_1a,
	SUM(IF(price_zone=2,volume,0)) AS vol_zone_2a,
	SUM(IF(price_zone=3,volume,0)) AS vol_zone_3a,
	SUM(IF(price_zone=4,volume,0)) AS vol_zone_4a,
	SUM(IF(price_zone=5,volume,0)) AS vol_zone_5a
FROM t1
GROUP BY 1