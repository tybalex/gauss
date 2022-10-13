import time
import logging
logging.basicConfig(level=logging.INFO)

sleeptime = 60
time.sleep(sleeptime)
logging.info(f"training: sleep for {sleeptime}")
