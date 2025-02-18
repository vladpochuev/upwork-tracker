from job_formatter import create_job_message
from topic_paser import get_first_topic_job

job = get_first_topic_job("telegram bot")
job_message = create_job_message(job)
print(job_message)
