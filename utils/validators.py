from utils.exceptions import ValidationError


def validate_file_size(size: int, max_upload_size_mb: int) -> None:
    if size > max_upload_size_mb * 1024 * 1024:
        raise ValidationError(
            f"Uploaded file exceeds {max_upload_size_mb} MB limit."
        )
