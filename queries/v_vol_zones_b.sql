DROP VIEW vol_zones_b;
CREATE VIEW vol_zones_b AS
WITH t0 AS (
	SELECT
		i1.product_id,
		i1.L1_name,
		i1.L2_DEPARTMENT_ID
	FROM input1 i1
	LEFT JOIN input2 i2 ON i1.product_id = i2.ArticleID
	WHERE i2.ArticleID IS NOT NULL AND i1.final_role IS NOT NULL
	AND i1.final_role NOT IN ('Fixed Prices', 'In-out/ Seasonal', 'Out of project')
),

t1 AS (
	SELECT
		t.*,
		t0.L1_name,
		t0.L2_DEPARTMENT_ID AS L2,
		i5.price_zone
	FROM table3 t LEFT JOIN t0 ON t.ID_Produktu = t0.product_id
	LEFT JOIN input5b i5 ON t.ID_Sklepu = i5.shop_id AND t0.L2_DEPARTMENT_ID = i5.dept
	WHERE t.ID_Sklepu IN (SELECT shop_id FROM input5a) AND
	t.ID_Produktu IN (SELECT product_id FROM t0)
)

SELECT
	ID_Produktu AS product_id,
	SUM(IIF(price_zone=410,volume,0)) AS vol_zone_410b,
	SUM(IIF(price_zone=420,volume,0)) AS vol_zone_420b,
	SUM(IIF(price_zone=430,volume,0)) AS vol_zone_430b,
	SUM(IIF(price_zone=440,volume,0)) AS vol_zone_440b,
	SUM(IIF(price_zone=450,volume,0)) AS vol_zone_450b,
	SUM(IIF(price_zone=502,volume,0)) AS vol_zone_502b,
	SUM(IIF(price_zone=505,volume,0)) AS vol_zone_505b,
	SUM(IIF(price_zone=506,volume,0)) AS vol_zone_506b,
	SUM(IIF(price_zone=507,volume,0)) AS vol_zone_507b,
	SUM(IIF(price_zone=900,volume,0)) AS vol_zone_900b,
	SUM(IIF(price_zone=11,volume,0)) AS vol_zone_11b,
	SUM(IIF(price_zone=12,volume,0)) AS vol_zone_12b,
	SUM(IIF(price_zone=13,volume,0)) AS vol_zone_13b,
	SUM(IIF(price_zone=21,volume,0)) AS vol_zone_21b,
	SUM(IIF(price_zone=22,volume,0)) AS vol_zone_22b,
	SUM(IIF(price_zone=23,volume,0)) AS vol_zone_23b,
	SUM(IIF(price_zone=1,volume,0)) AS vol_zone_1b,
	SUM(IIF(price_zone=211,volume,0)) AS vol_zone_211b,
	SUM(IIF(price_zone=212,volume,0)) AS vol_zone_212b,
	SUM(IIF(price_zone=213,volume,0)) AS vol_zone_213b,
	SUM(IIF(price_zone=300,volume,0)) AS vol_zone_300b,
	SUM(IIF(price_zone=301,volume,0)) AS vol_zone_301b,
	SUM(IIF(price_zone=302,volume,0)) AS vol_zone_302b
FROM t1
GROUP BY 1