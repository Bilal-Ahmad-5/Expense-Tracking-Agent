import pytesseract
import shutil
import subprocess

print("=== Tesseract OCR Check ===")

# 1. See if Python can find the binary in PATH
path_in_path = shutil.which("tesseract")
print(f"Found in PATH? {path_in_path}")

# 2. If not in PATH, try setting the path manually (edit this to your install location)
# Example Windows: r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Example macOS/Linux: "/usr/local/bin/tesseract"
pytesseract.pytesseract.tesseract_cmd = r"C:\codehub\Gen AI Projects\ETA\Expense-Tracking-Agent\venv\Lib\site-packages\pytesseract"

# 3. Print the path Python will try to use
print(f"Path pytesseract will use: {pytesseract.pytesseract.tesseract_cmd}")

# 4. Test calling the binary directly
try:
    result = subprocess.run(
        [pytesseract.pytesseract.tesseract_cmd, "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print("Tesseract version output:")
    print(result.stdout or result.stderr)
except FileNotFoundError:
    print("❌ ERROR: Tesseract binary not found at the given path.")
except Exception as e:
    print(f"❌ ERROR running Tesseract: {e}")
