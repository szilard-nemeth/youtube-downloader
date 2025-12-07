import os
import sys
from yt_dlp import YoutubeDL

def load_urls(file_path):
    """Read URLs from a file, ignoring empty lines and trimming whitespace."""
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def download_url(url, output_dir="downloads"):
    """
    Download a YouTube video or playlist using yt-dlp.
    Automatically expands playlists.
    """
    ydl_opts = {
        "outtmpl": os.path.join(output_dir, "%(playlist_title)s/%(title)s.%(ext)s"),
        "ignoreerrors": True,         # continue on errors
        "noplaylist": False,          # allow playlists
        "continuedl": True,           # resume partial downloads
        "retries": 10,                # retry network issues
        "concurrent_fragment_downloads": 5,
        # "format": "bv*+ba/b",         # best video + best audio
        "format": "bv*[height=1080]+ba/b"
    }

    with YoutubeDL(ydl_opts) as ydl:
        print(f"\n=== Downloading: {url} ===")
        ydl.download([url])

def main():
    if len(sys.argv) != 2:
        print("Usage: python download_youtube_from_file.py links.txt")
        sys.exit(1)

    links_file = sys.argv[1]

    if not os.path.exists(links_file):
        print(f"Error: File not found: {links_file}")
        sys.exit(1)

    urls = load_urls(links_file)

    if not urls:
        print("The file is empty — no URLs to process.")
        sys.exit(0)

    for url in urls:
        try:
            download_url(url)
        except Exception as e:
            print(f"Failed to download {url}: {e}")

if __name__ == "__main__":
    main()
