import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

import requests
import json
import pandas as pd


load_dotenv() # take environment variables from .env.

st.set_page_config(page_title="Your AI Sells Data Analyst")
st.header("Welcome to your AI Sells Data Analyst")
question_input = st.text_input("Ask your question here:")
hitme_button = st.button("Hit me")
# stdf = st.dataframe()

prompt_template = """
[Context]
As a Data Scientist expert in SQL and given a sales delta lake table that containts the daily sales of a sporting goods store.
You receive human written text requests to get information from the sales table. You need to generate the SQL statement to get the information requested.

The table has the following schema:
- sale_id
- product_name
- seller
- quantity_sold
- sale_date
- customer_name
- total_amount (in usd)
The path of the delta lake table is: "s3://bucket/sales".

When generating the query take into account the following:
1. The select statement follow the following format: Select * from delta.`s3://bucket/sales`
2. If you need to use a where clause to get the sales date minus some days, use the following format : sale_date >= date_sub(current_date(), 7)

Answer 'NoAnswer' if you do not know the answer.
[Request]
{request}
"""

def execute_query(sql_statement):

    # Replace the s3 path with the databricks path
    #
    sales_table_path = "s3://{aws_access}:{aws_secret}@mydev-databricks/deltalake/sales".format(
        aws_access=os.environ['AWS_ACCESS_KEY'], aws_secret=os.environ['AWS_SECRET_KEY']
    )

    sql_statement = sql_statement.replace('s3://bucket/sales', sales_table_path)

    # Execute the query in Databricks
    #
    url = "{databricks_api}/sql/statements/".format(databricks_api=os.environ['DATABRICKS_API'])

    payload = json.dumps({
        "warehouse_id": os.environ['DATABRICKS_WAREHOUSE_ID'],
        "statement": sql_statement,
        "wait_timeout": "50s"
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {databricks_token}'.format(databricks_token=os.environ['DATABRICKS_TOKEN'])
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    # Get the result of the query and return it as a dataframe
    #
    response_json = json.loads(response.text)
    columns = response_json['manifest']['schema']['columns']
    data = response_json['result']['data_array']
    column_names = [column['name'] for column in columns]
    df = pd.DataFrame(data, columns=column_names)

    return df    


def get_answer(question):
    genai.configure(api_key=os.environ['GOOGLE_API_KEY'])
    model=genai.GenerativeModel('gemini-pro')

    response = model.generate_content(
        prompt_template.format(request=question),    
        generation_config={"temperature": 0}
    )

    sql_statement = response.text.split('\n')[1:-1]
    sql_statement = '\n'.join(sql_statement)

    return sql_statement

if hitme_button:
    sql_statement = get_answer(question_input)
    # st.write(sql_statement)
    st.write(execute_query(sql_statement))
    
    

