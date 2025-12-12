# Custom exceptions for the application

class RedirectException(Exception):
    """Exception to trigger a redirect response"""
    def __init__(self, url: str):
        self.url = url
        super().__init__(f"Redirect to {url}")
