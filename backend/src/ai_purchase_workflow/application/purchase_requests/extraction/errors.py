class ExtractionError(ValueError):
    pass


class MalformedModelOutputError(ExtractionError):
    pass


class AmbiguousExtractionError(ExtractionError):
    pass
