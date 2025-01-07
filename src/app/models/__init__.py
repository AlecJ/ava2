
countries = []


class Session:
    def __init__(self, session_id):
        self.session_id = session_id
        self.players = []

    def __str__(self):
        return self.session_id

    def __repr__(self):
        return self.session_id

    def to_dict(self):
        return {
            'session_id': self.session_id
        }
