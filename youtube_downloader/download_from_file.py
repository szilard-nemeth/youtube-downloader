import os
import sys
from yt_dlp import YoutubeDL

def load_urls(file_path):
    """Read URLs from a file, ignoring empty lines and trimming whitespace."""
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]

def download_url(url, video_index=-1, total_videos=-1, output_dir="yt-dlp-downloads"):
    """
    Download a YouTube video or playlist using yt-dlp.
    Automatically expands playlists.
    :param total_videos:
    """
    if video_index != -1 and total_videos != -1:
        print(f"\n=== Downloading {video_index}/{total_videos}: {url} ===")

    ydl_opts = {
            "outtmpl": os.path.join(output_dir, "%(playlist_title)s/%(title)s.%(ext)s"),
            "ignoreerrors": True,         # continue on errors
            "noplaylist": False,          # allow playlists
            "continuedl": True,           # resume partial downloads
            "retries": 10,                # retry network issues
            "concurrent_fragment_downloads": 5,
            # "format": "bv*+ba/b",         # best video + best audio
            # "format": "bv*[height=1080]+ba/b",
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4" # forces MP4 output
        }

    with YoutubeDL(ydl_opts) as ydl:
        print(f"\n=== Downloading: {url} ===")
        ydl.download([url])

def main():
    if len(sys.argv) != 2:
        print("Usage: python download_youtube_from_file.py <file>")
        sys.exit(1)

    links_file = sys.argv[1]

    if not os.path.exists(links_file):
        print(f"Error: File not found: {links_file}")
        sys.exit(1)

    urls = load_urls(links_file)

    if not urls:
        print("The file is empty — no URLs to process.")
        sys.exit(0)

    total_videos = len(urls)
    for idx, url in enumerate(urls):
        try:
            output_dir = os.path.join(os.path.expanduser("~"), "yt-dlp-downloads")
            download_url(url, video_index=idx, total_videos=total_videos, output_dir=output_dir)
        except Exception as e:
            print(f"Failed to download {url}: {e}")

if __name__ == "__main__":
    main()
