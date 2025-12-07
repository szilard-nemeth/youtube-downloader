from __future__ import annotations

import argparse
import pathlib
import sys
import threading
from typing import List, Dict, Any, Optional

from youtube_downloader.cache import VideoTitleCache
from youtube_downloader.service import TitleService, YoutubeOps
from youtube_downloader.utils import LoggingUtils

try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init()
except Exception:
    # fallback to no color if colorama not installed
    class _C:
        def __getattr__(self, _): return ""
    Fore = Style = _C()

LOCK = threading.Lock()


def make_ydl_opts(cookiefile: Optional[str] = None,
                  use_browser_cookies: bool = False) -> Dict[str, Any]:

    ydl_opts: Dict[str, Any] = {
        # "retries": 10,                # retry network issues
        # "concurrent_fragment_downloads": 5,
        # avoid printing full debug stack by default
        "quiet": True,
        "verbose": False,
        'forcejson': True,      # Force JSON metadata extraction
        'skip_download': True,  # Don't download anything
        'ignore_no_formats_error': True,
        # use browser cookies automatically if requested
    }

    # Use browser cookies if requested
    if use_browser_cookies:
        # youtube extraction works with many browsers; we use chrome by default
        # yt-dlp accepts tuple for cookiesfrombrowser
        ydl_opts["cookiesfrombrowser"] = ("chrome",)

    # If user provided a cookiefile, add it (explicit cookie file takes precedence)
    if cookiefile:
        ydl_opts["cookiefile"] = cookiefile

    return ydl_opts

def load_urls(file_path: str) -> List[str]:
    p = pathlib.Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"URLs file not found: {file_path}")
    with p.open("r", encoding="utf-8") as fh:
        lines = [l.strip() for l in fh.readlines() if l.strip() and not l.strip().startswith("#")]
    return lines

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Get YouTube video titles by URLs (one per line)")
    p.add_argument("urls_file", help="Path to the text file containing URLs (one per line).")
    p.add_argument("--force-download", action="store_true",
                   help="Force download titles, even if title is cached")
    p.add_argument("--no-browser-cookies", action="store_true",
                   help="Don't attempt to read cookies from the browser automatically.")
    return p


def main(argv: Optional[List[str]] = None) -> None:
    args = build_argparser().parse_args(argv)
    level = LoggingUtils.init_with_basic_config(debug=True)

    try:
        urls = load_urls(args.urls_file)
    except FileNotFoundError as e:
        print(f"{Fore.RED}{e}{Style.RESET_ALL}")
        sys.exit(2)

    if not urls:
        print(f"{Fore.YELLOW}No URLs found in {args.urls_file}{Style.RESET_ALL}")
        sys.exit(0)

    # If user asked to skip browser cookies, disable that behavior
    use_browser_cookies = not args.no_browser_cookies
    ydl_opts = make_ydl_opts(use_browser_cookies=use_browser_cookies)

    cache = VideoTitleCache()
    title_service = TitleService(cache, ydl_opts, force_download=args.force_download)
    youtube_ops = YoutubeOps(cache, title_service)

    youtube_ops.get_video_titles(urls)

if __name__ == "__main__":
    main()
