SELECT
	i7.*,
	i8.category_role,
	IIF(i7.product_id IN (SELECT DISTINCT product_id FROM input_benchmark), 1, 0) AS benchmark_list,
    i10.sales_value,
	i10.unique_receipts,
	i10.avg_receipt_share,
	i10.shopping_frequency,
	i10.sales_margin,
	i10.nb_of_shops_with_sales,
	i10.avg_product_value,
	i10.promo_sales_share
FROM input_typology i7 LEFT JOIN input_category_role i8 ON i7.L2_DEPARTMENT_ID = i8.L2
LEFT JOIN input_scoring_factors i10 ON i7.product_id = i10.product_id