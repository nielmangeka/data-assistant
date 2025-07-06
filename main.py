from bq.bq_conn import BQConnection
from agent.tools import AgenConfig
from catalog.main import RedisConfig
import logging
import asyncio
import time

# Setting up logger to monitoring the process
logger = logging.getLogger(__name__) 
logger.setLevel(logging.DEBUG)

# Connect and get metadata data from BigQuery
bq_conn = BQConnection()
redis_conn = RedisConfig()

if __name__ == "__main__":

    def get_metadata():
        # metadata = bq_conn.fetch_bq_metadata() # Turn on if you want fetch the metadata directly from BQ
        metadata = redis_conn.main() # Fetch metadata from redis

        return metadata
    
    start_time = time.time()
    metadata = get_metadata() #asyncio.run(run_bq())
    end_time = time.time()

    runtime = end_time - start_time
    print(f'Runtime hit redis : {runtime:.4f}')
    
    question = input('What kind of data you are looking? : ')
    
    try:
        status = True
        while status:
            if metadata:
                logger.info('Got the metadata data')
                agen_conn = AgenConfig()
                table_sugg = agen_conn.catalog_assitant(metadata, question)
                print(table_sugg)
                status =False

            else:
                logger.error('No Data Found!')
                status = True
    
    except Exception as e:  
        logger.error('There is an issue while connect and fetch data from BigQuery' , e)