from datetime import datetime
import random
import psycopg2
from psycopg2.extras import execute_values
from faker import Faker

fake = Faker()

DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "26082001",  
    "host": "localhost",
    "port": 5432,
}

start_date = datetime(2025, 1, 1)
end_date = datetime(2025, 5, 31)

TOTAL_MAPPINGS = 500

try:
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # 1. Fetch valid IDs from promotion and product tables
    cursor.execute("SELECT promotion_id FROM promotion;")
    promotion_ids = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT product_id FROM product;")
    product_ids = [row[0] for row in cursor.fetchall()]

    print(f"Generating and inserting {TOTAL_MAPPINGS} promotion_product mappings...")

    # 2. Generate unique pairs to prevent duplicate key violations
    unique_pairs = set()
    mappings = []

    while len(mappings) < TOTAL_MAPPINGS:
        promo_id = random.choice(promotion_ids)
        prod_id = random.choice(product_ids)

        if (promo_id, prod_id) not in unique_pairs:
            unique_pairs.add((promo_id, prod_id))
            created_at = fake.date_time_between(start_date=start_date, end_date=end_date)
            mappings.append((promo_id, prod_id, created_at))

    # 3. Batch insert mappings
    insert_query = """
        INSERT INTO promotion_product (promotion_id, product_id, created_at)
        VALUES %s;
    """
    execute_values(cursor, insert_query, mappings)
    conn.commit()

    print(f"Successfully inserted {TOTAL_MAPPINGS} promotion_product records into PostgreSQL!")

    cursor.close()
    conn.close()

except Exception as error:
    print(f"Error while inserting promotion_product: {error}")