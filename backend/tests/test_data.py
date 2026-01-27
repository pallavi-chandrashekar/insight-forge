"""Test data generators and fixtures"""
import pandas as pd
from pathlib import Path


def create_sample_products_csv(file_path: str = "/tmp/test_products.csv"):
    """Create sample products CSV for testing"""
    df = pd.DataFrame({
        "product_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        "product_name": [
            "Laptop Pro 15", "Wireless Mouse", "Mechanical Keyboard",
            "27\" Monitor", "USB-C Hub", "Webcam HD",
            "Laptop Stand", "Wireless Headphones", "External SSD 1TB", "Tablet 10\""
        ],
        "category": [
            "Computers", "Accessories", "Accessories",
            "Monitors", "Accessories", "Accessories",
            "Accessories", "Audio", "Storage", "Computers"
        ],
        "price": [1299.99, 29.99, 89.99, 349.99, 49.99, 79.99, 39.99, 199.99, 149.99, 499.99],
        "stock": [50, 200, 150, 75, 300, 120, 180, 90, 100, 60],
        "rating": [4.5, 4.2, 4.7, 4.6, 4.3, 4.1, 4.4, 4.8, 4.6, 4.5],
        "reviews": [1250, 856, 432, 678, 234, 189, 345, 567, 890, 456]
    })
    df.to_csv(file_path, index=False)
    return df


def create_sample_sales_csv(file_path: str = "/tmp/test_sales.csv"):
    """Create sample sales CSV for testing"""
    df = pd.DataFrame({
        "order_id": range(1, 21),
        "customer_id": [1, 2, 3, 1, 4, 5, 2, 3, 1, 6, 7, 8, 4, 5, 9, 10, 2, 3, 1, 6],
        "customer_name": [
            "Alice Johnson", "Bob Smith", "Charlie Brown", "Alice Johnson", "David Lee",
            "Eve Martinez", "Bob Smith", "Charlie Brown", "Alice Johnson", "Frank White",
            "Grace Kim", "Henry Davis", "David Lee", "Eve Martinez", "Ivy Chen",
            "Jack Wilson", "Bob Smith", "Charlie Brown", "Alice Johnson", "Frank White"
        ],
        "product_id": [1, 2, 3, 4, 5, 6, 2, 3, 1, 7, 8, 9, 5, 6, 10, 1, 2, 4, 9, 7],
        "product_name": [
            "Laptop Pro 15", "Wireless Mouse", "Mechanical Keyboard", "27\" Monitor",
            "USB-C Hub", "Webcam HD", "Wireless Mouse", "Mechanical Keyboard",
            "Laptop Pro 15", "Laptop Stand", "Wireless Headphones", "External SSD 1TB",
            "USB-C Hub", "Webcam HD", "Tablet 10\"", "Laptop Pro 15", "Wireless Mouse",
            "27\" Monitor", "External SSD 1TB", "Laptop Stand"
        ],
        "quantity": [1, 2, 1, 1, 3, 1, 1, 2, 1, 2, 1, 1, 2, 1, 1, 2, 3, 1, 2, 1],
        "price": [1299.99, 29.99, 89.99, 349.99, 49.99, 79.99, 29.99, 89.99,
                 1299.99, 39.99, 199.99, 149.99, 49.99, 79.99, 499.99,
                 1299.99, 29.99, 349.99, 149.99, 39.99],
        "order_date": [
            "2025-01-15", "2025-01-15", "2025-01-16", "2025-01-16", "2025-01-17",
            "2025-01-17", "2025-01-18", "2025-01-18", "2025-01-19", "2025-01-19",
            "2025-01-20", "2025-01-20", "2025-01-21", "2025-01-21", "2025-01-22",
            "2025-01-22", "2025-01-23", "2025-01-23", "2025-01-24", "2025-01-24"
        ],
        "status": [
            "Delivered", "Delivered", "Shipped", "Delivered", "Processing",
            "Delivered", "Delivered", "Shipped", "Delivered", "Processing",
            "Delivered", "Shipped", "Processing", "Delivered", "Delivered",
            "Processing", "Delivered", "Shipped", "Delivered", "Processing"
        ]
    })
    df.to_csv(file_path, index=False)
    return df


def create_sample_customers_csv(file_path: str = "/tmp/test_customers.csv"):
    """Create sample customers CSV for testing"""
    df = pd.DataFrame({
        "customer_id": range(1, 11),
        "customer_name": [
            "Alice Johnson", "Bob Smith", "Charlie Brown", "David Lee", "Eve Martinez",
            "Frank White", "Grace Kim", "Henry Davis", "Ivy Chen", "Jack Wilson"
        ],
        "email": [
            "alice.j@example.com", "bob.smith@example.com", "charlie.b@example.com",
            "david.lee@example.com", "eve.m@example.com", "frank.w@example.com",
            "grace.k@example.com", "henry.d@example.com", "ivy.c@example.com",
            "jack.w@example.com"
        ],
        "city": [
            "New York", "San Francisco", "Chicago", "Boston", "Seattle",
            "Austin", "Denver", "Portland", "Los Angeles", "Miami"
        ],
        "state": ["NY", "CA", "IL", "MA", "WA", "TX", "CO", "OR", "CA", "FL"],
        "registration_date": [
            "2024-06-15", "2024-07-20", "2024-08-10", "2024-09-05", "2024-09-22",
            "2024-10-01", "2024-10-15", "2024-11-03", "2024-11-20", "2024-12-08"
        ],
        "total_orders": [5, 3, 4, 2, 2, 2, 1, 1, 1, 1],
        "total_spent": [3899.96, 269.95, 619.96, 199.98, 159.98, 79.98, 199.99, 149.99, 499.99, 1299.99],
        "customer_tier": ["Gold", "Silver", "Gold", "Bronze", "Bronze", "Bronze", "Bronze", "Bronze", "Silver", "Gold"]
    })
    df.to_csv(file_path, index=False)
    return df


def create_sample_employee_csv(file_path: str = "/tmp/test_employees.csv"):
    """Create sample employee CSV for testing"""
    df = pd.DataFrame({
        "employee_id": range(1, 16),
        "first_name": [
            "John", "Sarah", "Michael", "Emily", "David",
            "Jessica", "Robert", "Maria", "William", "Lisa",
            "James", "Jennifer", "Richard", "Patricia", "Thomas"
        ],
        "last_name": [
            "Doe", "Smith", "Johnson", "Williams", "Brown",
            "Jones", "Garcia", "Miller", "Davis", "Rodriguez",
            "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson"
        ],
        "email": [
            "john.doe@company.com", "sarah.smith@company.com", "michael.j@company.com",
            "emily.w@company.com", "david.b@company.com", "jessica.j@company.com",
            "robert.g@company.com", "maria.m@company.com", "william.d@company.com",
            "lisa.r@company.com", "james.m@company.com", "jennifer.h@company.com",
            "richard.l@company.com", "patricia.g@company.com", "thomas.w@company.com"
        ],
        "department": [
            "Engineering", "Sales", "Engineering", "Marketing", "HR",
            "Sales", "Engineering", "Marketing", "Finance", "Sales",
            "Engineering", "HR", "Finance", "Sales", "Engineering"
        ],
        "position": [
            "Senior Developer", "Sales Manager", "Developer", "Marketing Specialist", "HR Manager",
            "Sales Rep", "Senior Developer", "Content Writer", "Accountant", "Sales Rep",
            "Tech Lead", "Recruiter", "Financial Analyst", "Sales Manager", "Developer"
        ],
        "salary": [
            95000, 75000, 70000, 60000, 80000,
            55000, 100000, 58000, 72000, 52000,
            110000, 62000, 68000, 78000, 72000
        ],
        "hire_date": [
            "2020-01-15", "2019-03-22", "2021-06-10", "2022-02-14", "2018-09-05",
            "2021-11-30", "2019-05-20", "2022-07-18", "2020-10-12", "2023-01-25",
            "2018-02-28", "2021-04-16", "2020-08-07", "2019-12-03", "2022-09-21"
        ],
        "performance_rating": [4.5, 4.2, 4.0, 4.3, 4.6, 3.8, 4.7, 4.1, 4.4, 3.9, 4.8, 4.2, 4.3, 4.5, 4.0]
    })
    df.to_csv(file_path, index=False)
    return df


if __name__ == "__main__":
    """Generate all test data files"""
    print("Generating test data files...")

    create_sample_products_csv()
    print("✓ Created test_products.csv")

    create_sample_sales_csv()
    print("✓ Created test_sales.csv")

    create_sample_customers_csv()
    print("✓ Created test_customers.csv")

    create_sample_employee_csv()
    print("✓ Created test_employees.csv")

    print("\nAll test data files created successfully!")
