# Minimal imghdr shim for Python 3.13+ compatibility
# Provides imghdr.what(file, h=None) used by Telethon

MAGIC_HEADERS = [
	(b"\xFF\xD8\xFF", "jpeg"),
	(b"\x89PNG\r\n\x1a\n", "png"),
	(b"GIF87a", "gif"),
	(b"GIF89a", "gif"),
	(b"BM", "bmp"),
	(b"RIFF", None),  # could be webp or other RIFF-based; check further
]

WEBP_RIFF_FOURCC = b"WEBP"

def what(file, h=None):
	"""Return image type for file or bytes. Supports jpeg, png, gif, bmp, webp."""
	data = None
	if h is not None:
		data = h
	else:
		try:
			with open(file, "rb") as f:
				data = f.read(64)
		except Exception:
			return None
	if not data:
		return None
	for magic, fmt in MAGIC_HEADERS:
		if data.startswith(magic):
			if fmt is None:
				# Detect WEBP within RIFF header
				if len(data) >= 12 and data[8:12] == WEBP_RIFF_FOURCC:
					return "webp"
				return None
			return fmt
	return None


