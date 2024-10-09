import multiprocessing

bind = ':8080'
threads = multiprocessing.cpu_count()
timeout = 1200
limit_request_fields = 8190
worker_class = 'uvicorn.workers.UvicornWorker'
workers = (2 * multiprocessing.cpu_count()) + 1
