import json
from kafka import KafkaProducer

TOPIC_REGISTRATION = "registations"
TOPIC_LIKE = "likes"
TOPIC_VIEW = "views"
TOPIC_COMMENT = "comments"


class KafkaWriter:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=["kafka:29092"],
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )

    def _write(self, topic, event):
        self.producer.send(topic, event)
        self.producer.flush()

    def add_registration_event(self, user, time):
        event = {"user": user, "timestamp": time.isoformat()}
        self._write(TOPIC_REGISTRATION, event)

    def add_like_event(self, user, post_id, time):
        event = {
            "user": user,
            "post_id": post_id,
            "time": time.isoformat(),
        }
        self._write(TOPIC_LIKE, event)

    def add_view_event(self, user, post_id, time):
        event = {
            "user": user,
            "post_id": post_id,
            "time": time.isoformat(),
        }
        self._write(TOPIC_VIEW, event)

    def add_comment_event(self, user, post_id, comment, time):
        event = {
            "user": user,
            "post_id": post_id,
            "comment": comment,
            "time": time.isoformat(),
        }
        self._write(TOPIC_COMMENT, event)
