#Temporary file for development purposes. 
#It is used with vscode debugge

import subprocess
import os

# Set environment variables
os.environ["WORKERS"] = "1"
os.environ["WORKER_CLASS"] = "gevent"
os.environ["ACCESS_LOG"] = "-"
os.environ["ERROR_LOG"] = "-"
os.environ["WORKER_TEMP_DIR"] = "/tmp"
os.environ["SECRET_KEY"] = ""
os.environ["SKIP_DB_PING"] = "false"
os.environ["UPLOAD_FOLDER"] = "/var/uploads"
os.environ["DATABASE_URL"] = "mysql+pymysql://ctfd:ctfd@db/ctfd"
os.environ["REDIS_URL"] = "redis://cache:6379"
os.environ["LOG_FOLDER"] = "/var/log/CTFd"
os.environ["REVERSE_PROXY"] = "true"

# Execute the shell script
subprocess.run(["/bin/bash", "CTFD/dev-entrypoint.sh"])