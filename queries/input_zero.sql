SELECT
	i7.*,
	i8.category_role,
	IIF(i7.product_id IN (SELECT DISTINCT product_id FROM input9), 1, 0) AS benchmark_list,
	COALESCE(i10.sales_value_ly, 0) AS sales_value_ly,
	COALESCE(i10.unique_receipts_ly, 0) AS unique_receipts_ly,
	COALESCE(i10.avg_receipt_share_ly, 0) AS avg_receipt_share_ly,
	COALESCE(i10.shopping_frequency, 0) AS shopping_frequency,
	COALESCE(i10.sales_margin, 0) AS sales_margin,
	COALESCE(i10.nb_of_shops_with_sales, 0) AS nb_of_shops_with_sales,
	COALESCE(i10.avg_product_value, 0) AS avg_product_value,
	COALESCE(i10.promo_sales_share, 0) AS promo_sales_share
FROM input7 i7 LEFT JOIN input8 i8 ON i7.L2_DEPARTMENT_ID = i8.L2
LEFT JOIN input10 i10 ON i7.product_id = i10.product_id