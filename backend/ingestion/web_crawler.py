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

# WHAT: List of institutional notice board URLs to monitor across MAIT and affiliating university GGSIPU.
# WHY: Captures official circulars, examination schedules, fee deadlines, and admission announcements
#      published on both the college portal (mait.ac.in) and university portal (ipu.ac.in).
NOTICE_BOARD_URLS = [
    "https://www.mait.ac.in/index.php/notices",
    "https://www.mait.ac.in/notices.php",
    "https://mait.ac.in",
    "http://www.ipu.ac.in/notices.php",
    "https://ipu.ac.in/notices.php",
    "https://ipu.ac.in",
]

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

    for url in NOTICE_BOARD_URLS:
        try:
            resp = requests.get(url, headers=REQUEST_HEADERS, timeout=6)
            if resp.status_code != 200:
                continue

            soup = BeautifulSoup(resp.text, "html.parser")

            # Strategy 1: Find notice divs, tables, or list items with matching class tags
            notice_elements = soup.find_all(
                ["div", "tr", "li"],
                class_=re.compile(r'(notice|announcement|circular|news|item)', re.IGNORECASE)
            )

            # Strategy 2: If on a dedicated notice page or university table, also extract table rows containing links
            if "notices" in url.lower() or "ipu.ac.in" in url.lower():
                table_rows = soup.find_all("tr")
                for row in table_rows:
                    if row not in notice_elements:
                        cells = row.find_all(["td", "th"])
                        if len(cells) >= 2 and row.find("a"):
                            notice_elements.append(row)

            for el in notice_elements:
                title_el = el.find(["h3", "h4", "a", "strong", "p"])
                date_el = el.find(["span", "small", "td", "time"], class_=re.compile(r'(date|time)', re.IGNORECASE))

                text = el.get_text(separator=" ", strip=True)
                if len(text) < 15:
                    continue

                date_str = date_el.get_text(strip=True) if date_el else str(datetime.today().date())

                item_idx = len(all_notices) + 1
                all_notices.append({
                    "text": text,
                    "metadata": {
                        "source": f"{url}#notice_{item_idx}",
                        "date": date_str,
                        "department": "Academic Section",
                        "circular_number": "",
                        "ocr_method": "web_scrape"
                    }
                })

        except requests.exceptions.RequestException as req_err:
            print(f"[SCRAPER] Network request to {url} skipped ({req_err})")
        except Exception as exc:
            print(f"[SCRAPER] Parsing error for {url}: {exc}")

    # If live scraping returned results, optionally cache a snapshot
    if all_notices and os.path.exists(RAW_SCRAPED_DIR):
        cache_path = os.path.join(RAW_SCRAPED_DIR, f"scraped_{datetime.today().strftime('%Y%m%d')}.json")
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                json.dump(all_notices, f, indent=2)
        except Exception:
            pass

    # Merge cached historical notices
    cached = load_cached_scraped_files()
    all_notices.extend(cached)

    return all_notices
