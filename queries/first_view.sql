SELECT
    i1.*,
    i2.VAT,
    i2.CZ3N,
    i2.CZ3B,
    i2.CZ4N,
    i2.CZ4B,
    i2.Synonim,
    i2.Indeks,
    i2.med_auchan,
    i2.med_biedronka,
    i2.med_intermarche,
    i2.med_kaufland,
    i2.med_leclerc,
    i2.med_lidl,
    i2.med_netto,
    i2.med_rossmann,
    i3.margin_min,
    i3.margin_gama,
    i3.margin_komp,
    i3.margin_super_komp
FROM input1 i1
LEFT JOIN input2 i2 ON i1.IDProduktu = i2.ArticleID
LEFT JOIN input3 i3 ON i1.L4_GROUP_SUB_ID = i3.L4
WHERE i2.ArticleID IS NOT NULL AND i1."Final role" IS NOT NULL
-- AND (COALESCE(i2.med_auchan, 0) + COALESCE(i2.med_biedronka, 0) + COALESCE(i2.med_intermarche, 0) +
-- COALESCE(i2.med_kaufland, 0) + COALESCE(i2.med_leclerc, 0) + COALESCE(i2.med_lidl, 0) +
-- COALESCE(i2.med_netto, 0) + COALESCE(i2.med_rossmann, 0)) > 0