import redis
from rq import Worker, Queue, Connection

listen = ['default']

# Use your Redis Labs connection information
redis_url = 'redis://:kJchBWfmn3lc319JRFjWxGGMrX6ef6ib@redis-19735.c327.europe-west1-2.gce.redns.redis-cloud.com:19735'

conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()
