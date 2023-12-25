SELECT
	i7.*,
	i8.category_role,
	IIF(i7.product_id IN (SELECT DISTINCT product_id FROM input9), 1, 0) AS benchmark_list,
	i10.sales_value_ly,
	i10.unique_receipts_ly,
	i10.avg_receipt_share_ly,
	i10.shopping_frequency,
	i10.sales_margin,
	i10.nb_of_shops_with_sales,
	i10.avg_product_value,
	i10.promo_sales_share
FROM input7 i7 LEFT JOIN input8 i8 ON i7.L2_DEPARTMENT_ID = i8.L2
LEFT JOIN input10 i10 ON i7.product_id = i10.product_id