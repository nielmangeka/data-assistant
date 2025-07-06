import redis
import time

class RedisConfig():
    def __init__(self):
        self.host='redis-13711.c256.us-east-1-2.ec2.redns.redis-cloud.com'
        self.port = 13711
        self.db = 0
        self.username='default'
        self.password='OJPKy5djqIE2r1Na2b5DYctuCpei9bDa'
    
    def redis_conn(self):
        r_conn = redis.Redis(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            db=self.db
        )

        try:
            response = r_conn.ping()
            if response == True:
                return r_conn
            
        except redis.ConnectionError as e: 
            return None

    def main(self):
        r_conn = self.redis_conn()
        if r_conn:
            try:
                all_keys = r_conn.json().get('bigquery:schema') 
                return all_keys
            except Exception as e:
                return e
        else:
            print('Could not connect to Redis!')

# start_time = time.time()


# metadata = sync_metadata()
# print(metadata.main())


# end_time = time.time()
# runtime = end_time - start_time
# print(f'\n\nRuntime hit redis json : {runtime:.4f}')