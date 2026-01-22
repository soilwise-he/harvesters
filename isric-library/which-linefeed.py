# save as check_ris_newlines.py and run: python check_ris_newlines.py
import requests
import re

url = "https://library.wur.nl/WebQuery/isric/isric.ris"
params = {"q": "Advances Recientes en el Estudio Hidrico de los Climas"}
headers = {
    "User-Agent": "python-requests/2.x (detect-newlines-script)",
    "Accept": "*/*",
}

def fetch(url, params=None, timeout=15):
    try:
        r = requests.get(url, params=params, headers=headers, timeout=timeout)
        r.raise_for_status()
        return r
    except Exception as e:
        print("Failed to fetch:", e)
        return None

r = fetch(url, params=params)
if r is None:
    print("Download failed. If you're behind a proxy or the server blocks programmatic requests, try pasting the file content here or download it with your browser and re-run using the local file path.")
    raise SystemExit(1)

# get raw bytes then decode (let requests guess encoding)
text = r.text

# look for the first occurrence of three or more consecutive newline sequences
# we'll try to find the literal sequences to report which exact characters appear together
patterns = [
    ("\r\n", r"\r\n\r\n\r\n"),
    ("\n",   r"\n\n\n"),
    ("\r",   r"\r\r\r"),
]

found = None
for name, pat in patterns:
    if re.search(pat, text):
        found = pat
        break

# If none of the exact 3-occurences found, search generically for 3 or more newline-like separators
if not found:
    m = re.search(r'(?:\r\n|\r|\n){3,}', text)
    if m:
        found = m.group(0)  # the matched newline string(s)

# report what we found (repr so you can see escapes)
print("Detected newline block-separator (repr):", repr(found) if found else "None detected")

# robust splitting: split on any sequence of 3 or more newline characters (CR, LF, CRLF mixed)
blocks = re.split(r'(?:\r\n|\r|\n){3,}', text.strip())

print("Number of blocks found:", len(blocks))
print("----\nFirst block (truncated to 1000 chars):\n")
print(blocks[0][:1000])
