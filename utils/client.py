class Client():
    def __init__(self, url, token, data_source_id = None):
        self.url = url
        self.headers = {"Authorization": "Bearer " + token, 'Content-type': 'application/json'}
        self.data_source_id = data_source_id
