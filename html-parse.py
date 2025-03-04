import time

from job_formatter import create_job_message
from topic_paser import get_job_url, get_job

t0 = time.time()
job_url = get_job_url("telegram bot")
job = get_job(job_url)
job_message = create_job_message(job)
print(job_message)
print(time.time() - t0)
