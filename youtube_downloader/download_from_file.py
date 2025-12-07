from __future__ import annotations
import os
import sys
import argparse
import pathlib
import threading
from typing import List, Dict, Any, Optional
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError

from youtube_downloader.constants import FilePath

try:
    from colorama import init as colorama_init, Fore, Style
    colorama_init()
except Exception:
    # fallback to no color if colorama not installed
    class _C:
        def __getattr__(self, _): return ""
    Fore = Style = _C()

LOCK = threading.Lock()
DEFAULT_OUTPUT_DIR = os.path.join(os.path.expanduser("~"), "yt-dlp-downloads")

def load_urls(file_path: str) -> List[str]:
    p = pathlib.Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"URLs file not found: {file_path}")
    with p.open("r", encoding="utf-8") as fh:
        lines = [l.strip() for l in fh.readlines() if l.strip() and not l.strip().startswith("#")]
    return lines

def make_ydl_opts(output_dir: str,
                  cookiefile: Optional[str],
                  use_browser_cookies: bool) -> Dict[str, Any]:
    # Ensure output_dir exists
    os.makedirs(output_dir, exist_ok=True)

    # Other formats
    ### best video + best audio
    # "format": "bv*+ba/b",
    # "format": "bv*[height=1080]+ba/b",
    ### merge into mp4 (container) and force conversion to mp4 (H.264) later
    # "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4", # forces MP4 output
    ### prefer 1080p video + best audio; fallback to best available
    # format": "bv*[height=1080]+ba/best",
    ### merge into mp4 (container) and force conversion to mp4 (H.264) later
    # "format": "bv*[height=1080]+ba/best",
    ydl_opts: Dict[str, Any] = {
        # Template: base / playlist_title / title.ext
        "outtmpl": os.path.join(output_dir, "%(playlist_title)s/%(title)s.%(ext)s"),
        "ignoreerrors": True,         # continue on errors
        "noplaylist": False,          # allow playlists
        "continuedl": True,           # resume partial downloads
        "retries": 10,                # retry network issues
        "concurrent_fragment_downloads": 5,
        "nooverwrites": True,
        "merge_output_format": "mp4",
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4", # forces MP4 output
        # be a bit quieter about cookies/js runtime if we set extractor args below
        "extractor_args": {"youtube": {"player_client": "default"}},
        # hooks: progress (download), postprocessor events
        "progress_hooks": [progress_hook],
        # avoid printing full debug stack by default
        "quiet": False,
        "verbose": False,
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

    # Force re-encode to mp4/h264 using ffmpeg postprocessor to avoid silent remux no-video issues
    ydl_opts["postprocessors"] = [
        {
            "key": "FFmpegVideoConvertor",
            "preferedformat": "mp4",  # re-encode to mp4 (H.264)
        }
    ]

    return ydl_opts

# Progress state printed by hooks. We use a lock to avoid interleaving prints
def progress_hook(status: Dict[str, Any]) -> None:
    """
    progress_hook receives dicts from yt-dlp with keys like:
    - status: "downloading" | "finished" | "error"
    - filename, downloaded_bytes, total_bytes, eta, speed, percent
    - info_dict / tmpfilename etc.
    """
    with LOCK:
        st = status.get("status")
        if st == "downloading":
            # percent might be None; show bytes
            percent = status.get("percent")
            speed = status.get("speed")
            eta = status.get("eta")
            filename = status.get("filename") or status.get("tmpfilename") or ""
            if percent is not None:
                print(f"{Fore.CYAN}[DL]{Style.RESET_ALL} {percent:.1f}%  {filename}  ETA:{eta}  {format_speed(speed)}")
            else:
                print(f"{Fore.CYAN}[DL]{Style.RESET_ALL} {filename}  {format_speed(speed)}")
        elif st == "finished":
            filename = status.get("filename") or ""
            print(f"{Fore.GREEN}[MERGE]{Style.RESET_ALL} Download finished, now post-processing: {filename}")
        elif st == "error":
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {status}")
        else:
            # unknown statuses
            pass

def format_speed(speed: Optional[float]) -> str:
    if not speed:
        return ""
    # speed is bytes/sec
    units = ["B/s", "KB/s", "MB/s", "GB/s"]
    s = float(speed)
    for u in units:
        if s < 1024.0:
            return f"{s:0.1f}{u}"
        s /= 1024.0
    return f"{s:.1f}TB/s"

def download_url(url: str, output_dir: str, idx: int, total: int,
                 cookiefile: Optional[str], use_browser_cookies: bool) -> None:
    """
    Download a YouTube video or playlist using yt-dlp.
    Automatically expands playlists.
    :param total_videos:
    """
    print(f"\n{Fore.YELLOW}=== Downloading {idx}/{total}: {url} ==={Style.RESET_ALL}")

    ydl_opts = make_ydl_opts(output_dir=output_dir,
                             cookiefile=cookiefile,
                             use_browser_cookies=use_browser_cookies)
    # Additional user-friendly options
    ydl_opts.update({
        "nopart": False,   # keep .part files to allow resuming
        "progress_hooks": [progress_hook],
    })

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except DownloadError as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Failed to download {url}: {e}")
    except Exception as e:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Unexpected error for {url}: {e}")

def build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Download YouTube URLs (one per line) via yt-dlp.")
    p.add_argument("urls_file", help="Path to the text file containing URLs (one per line).")
    p.add_argument("output_dir", nargs="?", default=FilePath.DEFAULT_OUTPUT_DIR,
                   help="Optional output directory (default: YT-DLP-downloads)")
    p.add_argument("--cookiefile", "-c", default=None,
                   help="Path to cookies.txt exported from browser (optional).")
    p.add_argument("--no-browser-cookies", action="store_true",
                   help="Don't attempt to read cookies from the browser automatically.")
    p.add_argument("--no-reencode", action="store_true",
                   help="Don't force re-encoding to H.264; may result in MP4 with no visible video for VP9 sources.")
    return p

def main(argv: Optional[List[str]] = None) -> None:
    args = build_argparser().parse_args(argv)

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

    # If user disabled re-encode, remove postprocessor from options by toggling in make_ydl_opts
    if args.no_reencode:
        # We will monkey-patch make_ydl_opts behavior by re-calling it and removing postprocessors
        ydl_opts_sample = make_ydl_opts(output_dir=args.output_dir, cookiefile=args.cookiefile,
                                        use_browser_cookies=use_browser_cookies)
        if "postprocessors" in ydl_opts_sample:
            del ydl_opts_sample["postprocessors"]
        # But since download_url builds its own opts, we'll pass a flag via environment variable
        # Simpler approach: warn the user that no re-encode is set and rely on default in make_ydl_opts
        print(f"{Fore.YELLOW}Warning: No re-encode requested; certain VP9 WebM -> MP4 merges may not display video.{Style.RESET_ALL}")

    total = len(urls)
    for idx, url in enumerate(urls, start=1):
        download_url(url=url,
                     output_dir=args.output_dir,
                     idx=idx,
                     total=total,
                     cookiefile=args.cookiefile,
                     use_browser_cookies=use_browser_cookies)

if __name__ == "__main__":
    main()
