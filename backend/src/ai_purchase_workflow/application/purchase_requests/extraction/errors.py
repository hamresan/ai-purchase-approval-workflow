class ExtractionError(ValueError):
    pass


class MalformedModelOutputError(ExtractionError):
    pass


class AmbiguousExtractionError(ExtractionError):
    pass


class ModelUnavailableError(ExtractionError):
    """The configured model provider could not produce a usable response."""
