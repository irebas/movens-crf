DROP TABLE vol_zones;
CREATE TABLE vol_zones AS
WITH t0 AS (
	SELECT
		i1.IDProduktu,
		i1.L1_name
	FROM input1 i1
	LEFT JOIN input2 i2 ON i1.IDProduktu = i2.ArticleID
	WHERE i2.ArticleID IS NOT NULL AND i1."Final role" IS NOT NULL
	AND i1."Final role" NOT IN ('Fixed Prices', 'In-out/ Seasonal', 'Out of project')
),

t1 AS (
	SELECT
		t.*,
		t0.L1_name,
		i."Strefa PDK" AS PDK,
		i."Strefa PFT" AS PFT,
		i."Strefa Bazar" AS BAZAR,
		i."Strefa EPCS" AS EPCS,
		i."Strefa Tekstylia" AS TEKSTYLIA
	FROM table3 t LEFT JOIN input4 i ON t.ID_Sklepu = i.Store_nb
	LEFT JOIN t0 ON t.ID_Produktu = t0.IDProduktu
	WHERE t.ID_Sklepu IN (SELECT Store_nb FROM input4) AND
	t.ID_Produktu IN (SELECT IDProduktu FROM t0) -- IN (1549152, 612629, 717118)
),

t2 AS (
	SELECT
		ID_Produktu,
		'PDK' AS L1,
		PDK AS strefa,
		SUM(volume) AS volume
	FROM t1
	WHERE L1_name = 'PDK' AND PDK IS NOT NULL
	GROUP BY 1,2,3
	UNION ALL
	SELECT
		ID_Produktu,
		'PFT' AS L1,
		PFT AS strefa,
		SUM(volume) AS volume
	FROM t1
	WHERE L1_name = 'PFT' AND PFT IS NOT NULL
	GROUP BY 1,2,3
	UNION ALL
	SELECT
		ID_Produktu,
		'BAZAR' AS L1,
		BAZAR AS strefa,
		SUM(volume) AS volume
	FROM t1
	WHERE L1_name = 'BAZAR' AND BAZAR IS NOT NULL
	GROUP BY 1,2,3
	UNION ALL
	SELECT
		ID_Produktu,
		'EPCS' AS L1,
		EPCS AS strefa,
		SUM(volume) AS volume
	FROM t1
	WHERE L1_name = 'EPCS' AND EPCS IS NOT NULL
	GROUP BY 1,2,3
	UNION ALL
	SELECT
		ID_Produktu,
		'TEKSTYLIA' AS L1,
		TEKSTYLIA AS strefa,
		SUM(volume) AS volume
	FROM t1
	WHERE L1_name = 'TEKSTYLIA' AND TEKSTYLIA IS NOT NULL
	GROUP BY 1,2,3
),

t3 AS (
	SELECT
		ID_Produktu AS IDProduktu,
		SUM(IIF(strefa=1,volume,0)) AS vol_zone_1a,
		SUM(IIF(strefa=2,volume,0)) AS vol_zone_2a,
		SUM(IIF(strefa=3,volume,0)) AS vol_zone_3a,
		SUM(IIF(strefa=4,volume,0)) AS vol_zone_4a,
		SUM(IIF(strefa=5,volume,0)) AS vol_zone_5a
	FROM t2
	GROUP BY 1
)

SELECT * FROM t3