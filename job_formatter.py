import emoji

feature_map = {
    "hourly_rate": (":hourglass_not_done:", "Hourly Rate"),
    "budget": (":money_bag:", "Budget"),
    "experience_level": (":graduation_cap:", "Experience Level"),
    "project_type": (":pushpin:", "Project Type"),
    "duration": (":timer_clock:", "Duration"),
    "hours_per_week": (":stopwatch:", "Hours Per Week"),
    "location": (":round_pushpin:", "Location"),
}


def format_active_features(features):
    active_features = []
    for attr, (emj, label) in feature_map.items():
        value = getattr(features, attr)
        if value:
            feature = emoji.emojize(f"{emj} {label}: {value}")
            active_features.append(feature)

    return active_features


def create_job_message(job):
    message = ""

    message += emoji.emojize(":loudspeaker: " + job.title + "\n")
    message += emoji.emojize(":memo: " + (
        job.description[:297].strip() + "..." if len(job.description) > 300 else job.description.strip()) + "\n")

    job_features_list = format_active_features(job.features)
    for job_feature in job_features_list:
        message += job_feature + "\n"

    message += emoji.emojize("\n:link: " + job.link)

    return message
