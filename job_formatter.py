import emoji
import re

feature_map = {
    "hourly_rate": (":hourglass_not_done:", "Hourly Rate"),
    "budget": (":money_bag:", "Budget"),
    "experience_level": (":graduation_cap:", "Experience Level"),
    "project_type": (":pushpin:", "Project Type"),
    "duration": (":timer_clock:", "Duration"),
    "hours_per_week": (":stopwatch:", "Hours Per Week"),
    "location": (":house:", "Location"),
}


def format_active_features(features):
    active_features = []
    for attr, (emj, label) in feature_map.items():
        value = getattr(features, attr)
        if value:
            feature = emoji.emojize(f"{emj} {label}: <b>{value}</b>")
            active_features.append(feature)

    return active_features


def create_job_message(job, topic):
    message = ""

    message += "A new job in the topic <b>\"{}\"</b>:\n\n".format(topic)
    message += emoji.emojize(f":loudspeaker: <b>{job.title}</b>\n")
    message += emoji.emojize(f":memo: {trim_description(job.description)}\n\n")

    job_features_list = format_active_features(job.features)
    for job_feature in job_features_list:
        message += job_feature + "\n"
    message += "\n"

    message += emoji.emojize(f":link: {job.link}")

    return message


def trim_description(description):
    description = re.sub("\n+", "\n", description)
    if len(description) > 300:
        return description[:297].strip() + "..."
    return description.strip()
