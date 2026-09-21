"""
Web Scraper for MAIT institutional notice boards.
Runs as an OFFLINE scheduled batch job (run_ingestion.py) - never in query runtime path.
Fetches active circulars, deadlines, and announcements with local caching in data/raw/scraped/.
"""
import glob
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import requests

try:
    from config import RAW_SCRAPED_DIR
except ImportError:
    from backend.config import RAW_SCRAPED_DIR

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# WHAT: List of institutional notice board URLs to monitor across MAIT and affiliating university GGSIPU.
# WHY: Captures official circulars, examination schedules, fee deadlines, and admission announcements
#      published on both the college portal (mait.ac.in) and university portal (ipu.ac.in).
NOTICE_BOARD_URLS = [
    "https://www.mait.ac.in/index.php/notices",
    "https://www.mait.ac.in/notices.php",
    "https://mait.ac.in",
    "https://ipu.ac.in/notices.php",
    "https://ipu.ac.in/exam_notices.php",
]

# WHAT: Maximum number of recent notices to harvest per URL.
# WHY: Prevents historical notice dumps (IPU has 14,000+ notices dating to 2008) from overwhelming
#      the CPU embedding step; prioritizes the most recent semester/academic year circulars.
MAX_NOTICES_PER_URL = 100

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MAIT-Bot/1.0"
    )
}


def load_cached_scraped_files() -> List[Dict[str, Any]]:
    """
    Load any pre-scraped text or json notice files from data/raw/scraped/.
    Enables reproducible offline indexing when external websites are unreachable.
    """
    cached_notices: List[Dict[str, Any]] = []
    if not os.path.exists(RAW_SCRAPED_DIR):
        return cached_notices

    # Load .json scraped records
    for json_file in glob.glob(os.path.join(RAW_SCRAPED_DIR, "*.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    cached_notices.extend(data)
                elif isinstance(data, dict):
                    cached_notices.append(data)
        except Exception as e:
            print(f"[SCRAPER] Error reading cached json {json_file}: {e}")

    # Load .txt scraped records
    for txt_file in glob.glob(os.path.join(RAW_SCRAPED_DIR, "*.txt")):
        try:
            with open(txt_file, "r", encoding="utf-8") as f:
                text = f.read().strip()
                if text:
                    cached_notices.append({
                        "text": text,
                        "metadata": {
                            "source": os.path.basename(txt_file),
                            "date": str(datetime.today().date()),
                            "department": "Institutional Notices",
                            "circular_number": "",
                            "ocr_method": "web_scrape_cached"
                        }
                    })
        except Exception as e:
            print(f"[SCRAPER] Error reading cached text {txt_file}: {e}")

    return cached_notices


def scrape_notices() -> List[Dict[str, Any]]:
    """
    Scrape institutional notice boards and return list of notice dictionaries.
    Falls back to cached documents if network is unreachable or blocked.
    """
    all_notices: List[Dict[str, Any]] = []
    seen_texts: set = set()

    for url in NOTICE_BOARD_URLS:
        try:
            resp = requests.get(url, headers=REQUEST_HEADERS, timeout=10, verify=False)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            notice_elements = []

            # Strategy 1: Find notice divs, tables, or list items with matching class tags (limit to 150)
            class_elements = soup.find_all(
                ["div", "tr", "li"],
                class_=re.compile(r'(notice|announcement|circular|news|item)', re.IGNORECASE),
                limit=150
            )
            notice_elements.extend(class_elements)

            # Strategy 2: If on a dedicated notice page or university table, extract top recent table rows
            if "notices" in url.lower() or "ipu.ac.in" in url.lower():
                table_rows = soup.find_all("tr", limit=150)
                for row in table_rows:
                    cells = row.find_all(["td", "th"])
                    if len(cells) >= 2 and row.find("a"):
                        notice_elements.append(row)

            url_count = 0
            for el in notice_elements:
                if url_count >= MAX_NOTICES_PER_URL:
                    break

                title_el = el.find(["h3", "h4", "a", "strong", "p"])
                date_el = el.find(["span", "small", "td", "time"], class_=re.compile(r'(date|time)', re.IGNORECASE))

                text = el.get_text(separator=" ", strip=True)
                if len(text) < 15:
                    continue

                # Deduplicate by first 80 characters of text
                text_key = " ".join(text.lower().split()[:15])
                if text_key in seen_texts:
                    continue
                seen_texts.add(text_key)

                date_str = date_el.get_text(strip=True) if date_el else str(datetime.today().date())

                item_idx = len(all_notices) + 1
                dept_name = "Examination Division" if "exam" in url.lower() else "Academic Section"
                all_notices.append({
                    "text": text,
                    "metadata": {
                        "source": f"{url}#notice_{item_idx}",
                        "date": date_str,
                        "department": dept_name,
                        "circular_number": "",
                        "ocr_method": "web_scrape"
                    }
                })
                url_count += 1

        except requests.exceptions.RequestException as req_err:
            print(f"[SCRAPER] Network request to {url} skipped ({req_err})")
        except Exception as exc:
            print(f"[SCRAPER] Parsing error for {url}: {exc}")

    # If live scraping returned results, cache a snapshot for offline reproducibility
    if all_notices and os.path.exists(RAW_SCRAPED_DIR):
        cache_path = os.path.join(RAW_SCRAPED_DIR, f"scraped_{datetime.today().strftime('%Y%m%d')}.json")
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(all_notices, f, indent=2)
        except Exception:
            pass
    elif not all_notices:
        # Fallback to cached historical notices ONLY if live scraping yielded 0
        all_notices = load_cached_scraped_files()

    return all_notices
