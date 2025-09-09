from typing import Dict, Any
from PIL import Image
import io
import os
import sys

try:
	import pytesseract
	_TESS_AVAILABLE = True
	
	# Configure Tesseract for cross-platform compatibility
	try:
		# Check if we're running on Windows or Linux
		if os.name == 'nt':  # Windows
			# Try local Windows tesseract.exe first
			candidates = [
				os.path.join(os.getcwd(), 'tesseract.exe'),
				os.path.join(os.getcwd(), 'Tesseract-OCR', 'tesseract.exe'),
				os.path.join(os.getcwd(), 'bin', 'tesseract.exe')
			]
			for candidate in candidates:
				if os.path.exists(candidate):
					pytesseract.pytesseract.tesseract_cmd = candidate
					print(f"✅ Found Windows Tesseract binary at: {candidate}")
					break
			else:
				print("⚠️ No local tesseract.exe found, using system PATH")
		else:  # Linux/Unix (Docker/Render)
			# On Linux, tesseract should be available via system PATH
			try:
				# Test if tesseract is available
				import subprocess
				result = subprocess.run(['tesseract', '--version'], 
				                      capture_output=True, text=True, timeout=10)
				if result.returncode == 0:
					print(f"✅ Found system Tesseract: {result.stdout.split()[1] if result.stdout else 'Unknown version'}")
					# Set TESSDATA_PREFIX if available
					tessdata_prefix = os.environ.get('TESSDATA_PREFIX')
					if tessdata_prefix:
						print(f"✅ Using TESSDATA_PREFIX: {tessdata_prefix}")
				else:
					print("❌ System tesseract not working properly")
					_TESS_AVAILABLE = False
			except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
				print(f"❌ Tesseract not found on system: {e}")
				_TESS_AVAILABLE = False
	except Exception as e:
		print(f"⚠️ Tesseract configuration error: {e}")
		pass
except Exception as e:
	print(f"❌ Failed to import pytesseract: {e}")
	_TESS_AVAILABLE = False


def extract_text_from_image_bytes(image_bytes: bytes, lang: str = 'eng') -> Dict[str, Any]:
	"""
	Extract text from image bytes using Tesseract OCR via pytesseract.
	Returns dict with ok, text, error, engine flags. Gracefully handles missing tesseract binary.
	"""
	result: Dict[str, Any] = {"ok": False, "text": "", "error": None, "engine": {"pytesseract": _TESS_AVAILABLE}}
	if not _TESS_AVAILABLE:
		result["error"] = "pytesseract not installed"
		return result
	try:
		with Image.open(io.BytesIO(image_bytes)) as im:
			# Convert to RGB to normalize
			img = im.convert('RGB')
			text = pytesseract.image_to_string(img, lang=lang)
			result["ok"] = True
			result["text"] = text.strip()
			return result
	except pytesseract.TesseractNotFoundError:
		result["error"] = "Tesseract binary not found. Install Tesseract and ensure it's in PATH or place tesseract.exe in project root/Tesseract-OCR/."
		return result
	except Exception as e:
		result["error"] = str(e)
		return result
