from PIL import Image
import io

def resize_image(image_bytes, max_size=1024):
    """
    Resizes an image to have a maximum width/height of `max_size`
    while keeping the aspect ratio the same.

    Returns: resized image bytes (JPEG)
    """

    # Load image from bytes
    img = Image.open(io.BytesIO(image_bytes))

    # Convert to RGB (prevents problems if image is PNG with alpha channel)
    if img.mode != "RGB":
        img = img.convert("RGB")

    # Get original dimensions
    width, height = img.size

    # Compute the scale 
    scale = max(width, height) / max_size
    if scale < 1:
        return image_bytes

    new_width = int(width / scale)
    new_height = int(height / scale)

    # Resize image
    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Save resized image back to bytes
    output_buffer = io.BytesIO()
    img.save(output_buffer, format="JPEG", quality=90)

    return output_buffer.getvalue()

