DROP VIEW vol_zones_a;
CREATE VIEW vol_zones_a AS
WITH t0 AS (
	SELECT
		i1.product_id,
		i1.L1_SECTOR_ID
	FROM input1 i1
	LEFT JOIN input2 i2 ON i1.product_id = i2.ArticleID
	WHERE i2.ArticleID IS NOT NULL AND i1.final_role IS NOT NULL
	AND i1.final_role NOT IN ('Fixed Prices', 'In-out/ Seasonal', 'Out of project')
),

t1 AS (
	SELECT
		t.*,
		t0.L1_SECTOR_ID AS L1,
		i5.price_zone
	FROM table3 t LEFT JOIN t0 ON t.ID_Produktu = t0.product_id
	LEFT JOIN input5a i5 ON t.ID_Sklepu = i5.shop_id AND t0.L1_SECTOR_ID = i5.dept
	WHERE t.ID_Sklepu IN (SELECT shop_id FROM input5a) AND
	t.ID_Produktu IN (SELECT product_id FROM t0)
)

SELECT
	ID_Produktu AS product_id,
	SUM(IIF(price_zone=1,volume,0)) AS vol_zone_1a,
	SUM(IIF(price_zone=2,volume,0)) AS vol_zone_2a,
	SUM(IIF(price_zone=3,volume,0)) AS vol_zone_3a,
	SUM(IIF(price_zone=4,volume,0)) AS vol_zone_4a,
	SUM(IIF(price_zone=5,volume,0)) AS vol_zone_5a
FROM t1
GROUP BY 1