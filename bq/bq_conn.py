
from google.cloud import bigquery
from google.oauth2.service_account import Credentials
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class BQConnection():
    def __init__(self):
        # Set up BigQuery client
        self.SCOPES = ['https://www.googleapis.com/auth/cloud-platform'] 
        self.credens = Credentials.from_service_account_file(
            './creds/creds.json',
            scopes=self.SCOPES
        )

        self.project_id = 'indosat-463417'
        self.dataset_id = 'raw'
        self.client = bigquery.Client(credentials=self.credens, project=self.project_id)
        self.dataset_ref = self.client.dataset(self.dataset_id, project=self.project_id)
    
    def bq_parser(self, raw_data):
        parse_data = [dict(row) for row in raw_data]
        
        return parse_data

    def fetch_bq_metadata(self):
        query_func = f"""
        SELECT
            table_name as table_name,
            option_value AS table_desc,
            -- c.column_name as column_name,
            -- c.description as column_description
            ARRAY_AGG(STRUCT(column_name AS column_name, c.description AS columns_desc)) AS column_info
        FROM `raw.INFORMATION_SCHEMA.TABLES` t
        LEFT JOIN `raw.INFORMATION_SCHEMA.TABLE_OPTIONS` o 
            USING (table_name)
        LEFT JOIN `raw.INFORMATION_SCHEMA.COLUMN_FIELD_PATHS` c
            USING(table_name)
        WHERE option_name = 'description'
        GROUP BY 1,2;
        """

        try:
            query_job = self.client.query(query_func).result()
            data_formatted = self.bq_parser(query_job)

        except Exception as e:
            logger.critical('Cannot fetch data from BigQuery', e)
            
        return data_formatted