from typing import Dict, Any, Optional
from PIL import Image
import io
import hashlib


def _sha256_bytes(data: bytes) -> str:
	sha = hashlib.sha256()
	sha.update(data)
	return sha.hexdigest()


def analyze_image_bytes(image_bytes: bytes, max_size: int = 2048) -> Dict[str, Any]:
	"""
	Analyze an image from raw bytes.
	- Safely opens via Pillow
	- Extracts format, size, mode
	- Generates a content hash
	- Computes a coarse color histogram (16-bin per channel if RGB)
	- Optionally downsizes large images to control memory
	"""
	info: Dict[str, Any] = {
		"ok": False,
		"error": None,
		"format": None,
		"size": None,
		"mode": None,
		"sha256": None,
		"histogram": None
	}
	try:
		info["sha256"] = _sha256_bytes(image_bytes)
		with Image.open(io.BytesIO(image_bytes)) as im:
			# Verify basic integrity
			im.verify()
		# Re-open since verify() leaves file in an unusable state for load
		with Image.open(io.BytesIO(image_bytes)) as im2:
			im2.load()
			fmt = im2.format
			size = im2.size
			mode = im2.mode

			# Downscale if very large
			if max(size) > max_size:
				scale = max_size / float(max(size))
				new_size = (max(1, int(size[0] * scale)), max(1, int(size[1] * scale)))
				im2 = im2.resize(new_size)

			# Compute histogram (coarse)
			hist_summary: Optional[Dict[str, Any]] = None
			if mode in ("RGB", "RGBA"):
				if mode == "RGBA":
					im3 = im2.convert("RGB")
				else:
					im3 = im2
				# Reduce to 4 bits per channel (16 bins) per channel
				# Build compact histogram: 16 bins for R,G,B each
				bins = 16
				step = 256 // bins
				r_bins = [0] * bins
				g_bins = [0] * bins
				b_bins = [0] * bins
				for r, g, b in im3.getdata():
					r_bins[r // step] += 1
					g_bins[g // step] += 1
					b_bins[b // step] += 1
				hist_summary = {
					"bins": bins,
					"r": r_bins,
					"g": g_bins,
					"b": b_bins
				}
			else:
				# For other modes, fallback to global histogram length
				h = im2.histogram()
				hist_summary = {"length": len(h)}

			info.update({
				"ok": True,
				"format": fmt,
				"size": size,
				"mode": mode,
				"histogram": hist_summary
			})
	except Exception as e:
		info["ok"] = False
		info["error"] = str(e)
	return info


