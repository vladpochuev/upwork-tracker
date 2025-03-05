import time

from job_formatter import create_job_message
from topic_paser import get_job_url, get_job

t0 = time.time()

topic = "telegram bot"
job_url = get_job_url(topic)
job = get_job(job_url)
job_message = create_job_message(job, topic)

print(job_message)
print(time.time() - t0)
