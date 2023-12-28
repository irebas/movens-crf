WITH t0 AS (
	SELECT
		i1.product_id,
		i1.L1_name,
		i1.L2_DEPARTMENT_ID
	FROM `pric-labo.pricing_app.input_base` i1
	LEFT JOIN `pric-labo.pricing_app.input_price_reports` i2 ON i1.product_id = i2.product_id
	WHERE i2.product_id IS NOT NULL AND i1.final_role IS NOT NULL
	AND i1.final_role NOT IN ('Fixed Prices', 'In-out/ Seasonal', 'Out of project')
),

t1 AS (
	SELECT
		t.*,
		t0.L1_name,
		t0.L2_DEPARTMENT_ID AS L2,
		i5.price_zone
	FROM `pric-labo.pricing_app.input_volume` t LEFT JOIN t0 ON t.product_id = t0.product_id
	LEFT JOIN `pric-labo.pricing_app.input_price_zone_b` i5 ON t.shop_id = i5.shop_id AND t0.L2_DEPARTMENT_ID = i5.dept
	WHERE t.shop_id IN (SELECT shop_id FROM `pric-labo.pricing_app.input_price_zone_a`) AND
	t.product_id IN (SELECT product_id FROM t0)
)

SELECT
	product_id,
	SUM(IF(price_zone=410,volume,0)) AS vol_zone_410b,
	SUM(IF(price_zone=420,volume,0)) AS vol_zone_420b,
	SUM(IF(price_zone=430,volume,0)) AS vol_zone_430b,
	SUM(IF(price_zone=440,volume,0)) AS vol_zone_440b,
	SUM(IF(price_zone=450,volume,0)) AS vol_zone_450b,
	SUM(IF(price_zone=502,volume,0)) AS vol_zone_502b,
	SUM(IF(price_zone=505,volume,0)) AS vol_zone_505b,
	SUM(IF(price_zone=506,volume,0)) AS vol_zone_506b,
	SUM(IF(price_zone=507,volume,0)) AS vol_zone_507b,
	SUM(IF(price_zone=900,volume,0)) AS vol_zone_900b,
	SUM(IF(price_zone=11,volume,0)) AS vol_zone_11b,
	SUM(IF(price_zone=12,volume,0)) AS vol_zone_12b,
	SUM(IF(price_zone=13,volume,0)) AS vol_zone_13b,
	SUM(IF(price_zone=21,volume,0)) AS vol_zone_21b,
	SUM(IF(price_zone=22,volume,0)) AS vol_zone_22b,
	SUM(IF(price_zone=23,volume,0)) AS vol_zone_23b,
	SUM(IF(price_zone=1,volume,0)) AS vol_zone_1b,
	SUM(IF(price_zone=211,volume,0)) AS vol_zone_211b,
	SUM(IF(price_zone=212,volume,0)) AS vol_zone_212b,
	SUM(IF(price_zone=213,volume,0)) AS vol_zone_213b,
	SUM(IF(price_zone=300,volume,0)) AS vol_zone_300b,
	SUM(IF(price_zone=301,volume,0)) AS vol_zone_301b,
	SUM(IF(price_zone=302,volume,0)) AS vol_zone_302b
FROM t1
GROUP BY 1