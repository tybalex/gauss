import time
import logging
logging.basicConfig(level=logging.INFO)

while True:
    sleeptime = 60
    time.sleep(sleeptime)
    logging.info(f"inferencing: sleep for {sleeptime}")
