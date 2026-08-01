class MinIOClient:
    def __init__(self, endpoint: str = "localhost:9000", access_key: str = "minioadmin", secret_key: str = "minioadmin"):
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key

    def upload(self, file_path: str, object_name: str) -> str:
        return f"{self.endpoint}/{object_name}"
