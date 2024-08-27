workers = 1
worker_connections = 500
timeout = 300
bind = "0.0.0.0:{{port}}"
accesslog = "access.log"
errorlog = "error.log"
loglevel = "info"