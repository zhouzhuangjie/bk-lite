import base64
from pathlib import Path
from typing import Optional


def image_to_base64(image_path: str, log_file: str = "base64.log") -> Optional[str]:
    """
    Convert an image file to base64 string and save to log file.

    Args:
        image_path (str): Path to the image file
        log_file (str): Path to save the base64 result

    Returns:
        Optional[str]: Base64 encoded string of the image, or None if conversion fails
    """
    try:
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

            # Save to log file
            with open(log_file, "w") as log:
                log.write(encoded_string)

            return encoded_string

    except Exception as e:
        print(f"Error converting image to base64: {e}")
        return None


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) != 2:
        print("Usage: python img_to_base64.py <image_path>")
        sys.exit(1)

    result = image_to_base64(sys.argv[1])
    if result:
        print("Base64 result has been saved to base64.log")