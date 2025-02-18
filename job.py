class JobFeatures:
    def __init__(self, features):
        self.hours_per_week = features.get("clock-hourly")
        self.duration = features.get("duration2")
        self.experience_level = features.get("expertise")
        self.hourly_rate = features.get("clock-timelog")
        self.budget = features.get("fixed-price")
        self.location = features.get("local")
        self.project_type = features.get("briefcase-outlined")


class Job:
    def __init__(self, link, title, description, features):
        self.link = link
        self.title = title
        self.description = description
        self.features = features
