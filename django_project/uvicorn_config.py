# uvicorn_config.py

# ASGI app path
app = "progcomp.asgi:application"  # replace with your ASGI app

# Server options
host = "0.0.0.0"
port = 8000
log_level = "info"
workers = 9       
reload = False     
proxy_headers = True
