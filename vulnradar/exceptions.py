class VulnException(Exception):
    """Base exception for VulnRadar."""
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(self.message)

class InvalidAPIKeyException(VulnException):
    """Raised when an invalid API key is provided."""
    def __init__(self, message="Invalid API key provided."):
        self.message = message
        self.code = 401
        super().__init__(self.message, self.code)
        
class RateLimitedException(VulnException):
    """Raised when the API rate limit is exceeded."""
    def __init__(self, message="API rate limit exceeded. Please try again later."):
        self.message = message
        self.code = 429
        super().__init__(self.message, self.code)

class InvalidRequestException(VulnException):
    """Raised when an invalid request is made to the API."""
    def __init__(self, message="Invalid request. Please check your parameters and try again."):
        self.message = message
        self.code = 400
        super().__init__(self.message, self.code)
        
class ScanNotFoundException(VulnException):
    """Raised when a requested scan is not found."""
    def __init__(self, message="Scan not found. Please check the scan ID and try again."):
        self.message = message
        self.code = 404
        super().__init__(self.message, self.code)