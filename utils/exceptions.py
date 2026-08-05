class AppError(Exception):
    """Base exception for application-level errors."""


class ConfigurationError(AppError):
    pass


class ValidationError(AppError):
    pass


class FileProcessingError(AppError):
    pass


class TranslationError(AppError):
    pass


class SpeechGenerationError(AppError):
    pass
