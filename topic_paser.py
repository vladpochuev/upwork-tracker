import cloudscraper
from bs4 import BeautifulSoup

from job import *


def get_html(url):
    scraper = cloudscraper.create_scraper()
    html = scraper.get(url).text
    return html


def get_job_url(topic_name):
    topic_url = f"https://www.upwork.com/nx/search/jobs/?q={topic_name}"
    topic_html = get_html(topic_url)
    topic_soup = BeautifulSoup(topic_html, "html.parser")
    domain = "https://www.upwork.com"
    topic_header = topic_soup.find(class_="job-tile-header d-flex align-items-start")
    relative_url = topic_header.find("a")["href"]

    return domain + relative_url


def collect_features_to_dict(features):
    dictionary = {}

    for feature in features:
        feature_name = feature.find("div", class_="air3-icon md")["data-cy"]
        if feature_name == "clock-timelog":
            amounts = feature.find_all("strong")
            amount_from = amounts[0].text.strip()
            amount_to = amounts[1].text.strip()
            dictionary[feature_name] = amount_from + "-" + amount_to
        else:
            dictionary[feature_name] = feature.find("strong").text.strip()

    return dictionary


def is_job_private(job_html):
    try:
        job_soup = BeautifulSoup(job_html, "html.parser")
        job_private_text = job_soup.find("main", id="main").find("div", class_="reason-text").find("h4").text
        return job_private_text.strip() == "This job is a private listing."
    except Exception as e:
        print(e)
        return False


def get_job(job_url):
    job_html = get_html(job_url)
    job_soup = BeautifulSoup(job_html, "html.parser")

    try:
        job_title = job_soup.find("header", class_="air3-card-section py-4x").find("h4").text
        job_description = (job_soup.find("section", class_="air3-card-section py-4x")
                           .find("p", class_="text-body-sm")
                           .text)

        raw_features = job_soup.find("ul", class_="features list-unstyled m-0").find_all("li")
        features_dict = collect_features_to_dict(raw_features)

        job_features = JobFeatures(features_dict)
        return Job(job_url, job_title, job_description, job_features)
    except Exception as e:
        if is_job_private(job_html):
            print("Job is private")
        else:
            print(e)

        return None
