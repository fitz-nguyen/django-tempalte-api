import logging
import os
import tempfile
import time
from multiprocessing import Process

import psycopg2
import psycopg2.extensions
import requests
from django.conf import settings

# Create a temporary file for logging
log_file = tempfile.NamedTemporaryFile(mode="w", delete=False)
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.local"

logging.basicConfig(
    filename=log_file.name, filemode="w", format="%(asctime)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S"
)


def run_sub_process():
    if os.fork() != 0:  # <--
        logging.warning("Os.fork != 0")

    conn = psycopg2.connect(
        dbname=settings.DATABASES["default"]["NAME"],
        user=settings.DATABASES["default"]["USER"],
        password=settings.DATABASES["default"]["PASSWORD"],
        host=settings.DATABASES["default"]["HOST"],
    )
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    curs = conn.cursor()
    curs.execute("LISTEN sync_contact_completed_channel;")

    logging.info("Waiting for notifications on channel 'sync_contact_completed_channel'")
    while True:
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            logging.info("Got NOTIFY:", notify.pid, notify.channel, notify.payload)

            # Make a POST request to the Django service
            url = f"{settings.BASE_URL}/v1/dashboard/sync-contact-hook/"
            data = {"sync_contact_id": notify.payload}

            response = requests.post(url, data=data)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                logging.info("Request successful!")
            else:
                logging.error("Request failed with status code:", response.status_code)

            # Periodically flush the log file to write log messages to disk
            if time.time() % 60 == 0:  # Flush every 60 seconds
                log_file.flush()


if __name__ == "__main__":
    p = Process(target=run_sub_process)
    p.start()
    p.join()
