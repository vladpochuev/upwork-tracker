import cloudscraper
from bs4 import BeautifulSoup
from job import *


def get_soup(url):
    scraper = cloudscraper.create_scraper()
    html = scraper.get(url).text
    return BeautifulSoup(html, "html.parser")


def get_job_url(url):
    topic_soup = get_soup(url)
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


def get_first_topic_job(topic_name):
    topic_url = f"https://www.upwork.com/nx/search/jobs/?q={topic_name}"
    job_link = get_job_url(topic_url)
    job_soup = get_soup(job_link)

    job_title = job_soup.find("header", class_="air3-card-section py-4x").find("h4").text
    job_description = job_soup.find("section", class_="air3-card-section py-4x").find("p", class_="text-body-sm").text

    raw_features = job_soup.find("ul", class_="features list-unstyled m-0").find_all("li")
    features_dict = collect_features_to_dict(raw_features)

    job_features = JobFeatures(features_dict)
    return Job(job_link, job_title, job_description, job_features)
