from pyspark.sql import Row
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, DateType
from datetime import datetime, timedelta
import random

# Define the schema for the DataFrame
schema = StructType([
    StructField("sale_id", IntegerType(), True),
    StructField("product_name", StringType(), True),
    StructField("seller", StringType(), True),
    StructField("quantity_sold", IntegerType(), True),
    StructField("sale_date", DateType(), True),
    StructField("customer_name", StringType(), True),
    StructField("total_amount", FloatType(), True)
])

sellers = ["John Smith", "Jane Johnson", "Michael Williams", "Emma Jones", "Robert Brown", "Olivia Davis", "William Miller", "Sophia Wilson", "David Moore", "Ava Taylor"]

hiking_goods = [
    "Hiking boots",
    "Backpack",
    "Trekking poles",
    "Water bottle",
    "Hiking socks",
    "Headlamp",
    "Rain jacket",
    "Map and compass",
    "Tent",
    "First aid kit"
]

# Generate 100 rows of sample data using a loop
data = []
for i in range(1, 501):
    data.append(Row(
        sale_id=i,
        product_name=hiking_goods[random.randint(0, len(hiking_goods)-1)] ,
        seller=sellers[random.randint(0, len(sellers)-1)] ,
        quantity_sold=(i % 10) + 1,
        sale_date=(datetime.now() - timedelta(days=random.randint(0,14))).date(),
        customer_name=f"Customer {i}",
        total_amount=float((i % 5 + 1) * 20)
    ))

# Create a DataFrame using the generated data and schema
df = spark.createDataFrame(data, schema=schema)

# Display the DataFrame
display(df)