bind = 'unix:/var/www/swoogo/swoogo.sock'
backlog = 2048
workers = 1
worker_class = 'sync'
worker_connections = 100
timeout = 30
keepalive = 2
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%({x-forwarded-for}i)s %(l)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
worker_tmp_dir = '/dev/shm'
no_sendfile = True
capture_output = True
user = 1004
group = 1004