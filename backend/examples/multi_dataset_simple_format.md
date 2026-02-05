# E-Commerce Analytics

Complete e-commerce analytics spanning orders, customers, and products data. This context helps you analyze sales performance, customer behavior, and product trends.

## Datasets

- Orders (id: order-dataset-uuid-here)
- Customers (id: customer-dataset-uuid-here)
- Products (id: product-dataset-uuid-here)

## Relationships

- Orders → Customers via customer_id
- Orders → Products via product_id

## Overview

This multi-dataset context integrates three key datasets:

### Orders Dataset
Contains all order transactions including:
- Order ID and timestamps
- Customer and product references
- Quantities and amounts
- Order status

### Customers Dataset
Customer information including:
- Contact details
- Signup dates
- Customer segments (VIP, Regular, New)

### Products Dataset
Product catalog with:
- Product names and categories
- Pricing information
- Inventory status

## Key Relationships

**Order → Customer**: Each order is placed by exactly one customer. Use `customer_id` to join orders to customer information.

**Order → Product**: Each order line references one product. Use `product_id` to join orders to product details.

## Common Analysis Questions

### Cross-Dataset Analysis
- Show total revenue by customer segment
- What are the top 10 products by revenue?
- Show average order value for VIP customers
- Which product categories generate the most revenue?
- Show customer lifetime value distribution

### Customer Analytics
- List all VIP customers
- Show customer purchase frequency
- Identify customers who haven't ordered recently
- Compare spending by customer segment

### Product Analytics
- Show products in the Electronics category
- List best-selling products this month
- Show revenue by product category
- Identify slow-moving inventory

### Sales Analytics
- Show orders from the last 30 days
- Compare this month's sales to last month
- Show daily revenue trends
- Analyze average order value over time

## Key Metrics to Track

- **Total Revenue**: Sum of all order amounts
- **Average Order Value**: Mean transaction value
- **Customer Lifetime Value**: Total revenue per customer
- **Repeat Purchase Rate**: % of customers with multiple orders
- **Revenue by Category**: Sales breakdown by product type

## Analysis Tips

1. **Filter by Customer Segment**: Use VIP, Regular, or New customer filters to compare behavior
2. **Time-Based Analysis**: Look at trends over days, weeks, or months
3. **Category Performance**: Compare revenue and units sold across product categories
4. **Customer Cohorts**: Analyze customers by signup date to see retention patterns
