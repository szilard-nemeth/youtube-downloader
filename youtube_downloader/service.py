import enum
import logging
import re
from typing import Dict, Any, List, Tuple, Optional
from pythoncommons.url_utils import UrlUtils
from yt_dlp import YoutubeDL

from youtube_downloader.cache import VideoTitleCache
from youtube_downloader.html_utils import HtmlParser
import logging
LOG = logging.getLogger(__name__)

class YoutubeOps:
    def __init__(self,
                 cache: VideoTitleCache,
                 title_service: 'TitleService'):
        self._cache = cache
        self._title_service = title_service

    def get_video_titles(self, urls: List[str]):
        result = self._title_service.fetch_titles(urls)
        self._cache.save()

        LOG.info("PRINTING FINAL RESULTS...")
        for url, title in result.items():
            LOG.info("URL: %s, title: %s", url, title)


class TitleProvider(enum.Enum):
    BEAUTIFULSOUP = 'beautifulsoup'
    YT_DLP = 'yt-dlp'


class TitleService:
    def __init__(self, cache: VideoTitleCache, ydl_opts, provider=TitleProvider.YT_DLP, force_download=False):
        # The service holds the cache dependency
        self._ydl_opts = ydl_opts
        self._cache = cache
        if provider == TitleProvider.YT_DLP:
            self._title_provider = self.yt_dlp_title_provider
        elif provider == TitleProvider.BEAUTIFULSOUP:
            self._title_provider = self.bs_title_provider
        self._force_download = force_download

    def bs_title_provider(self, url: str):
        return HtmlParser.get_title_from_url(url)

    def yt_dlp_title_provider(self, url: str):
        with YoutubeDL(self._ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('title')

    def fetch_titles(self, urls: List[str]):
        """
        Iterates through all checklists in a board to fetch and cache URL titles.
        :param urls:
        """
        # Ensure the cache is used with a context manager if possible, or managed externally
        # to ensure it saves/closes correctly.

        result = {}
        total_urls = len(urls)
        for idx, url in enumerate(urls):
            LOG.info("[%d / %d] Fetching titles for url: %s ", idx + 1, total_urls, url)
            url_title = None
            try:
                # 1. Identify URL
                url = UrlUtils.extract_from_str(url)
            except:
                url = None
            if url:
                # 2. Get from cache or fetch (ALL cache interaction is here)
                # Uncomment to delete from cache
                # del self._cache._shelf["https://chatgpt.com/c/6872d253-faf8-8007-8ad8-6c144b31ce50"]
                url_title = self._cache.get(url)
                if self._force_download:
                    # Pretend URL title is not cached when force download is enabled
                    url_title = None
                if not url_title:
                    # Fetch title of URL
                    url_title = self._title_provider(url)
                    if url_title:
                        url_title = self._process_fetched_url_title(url, url_title)
                else:
                    # Read from cache (still need to clean old titles if needed)
                    new_url_title = re.sub(r'[\n\t\r]+', ' ', url_title)
                    if url_title != new_url_title:
                        self._cache.put(url, new_url_title)
                    url_title = new_url_title
            if url_title:
                result[url] = url_title

        # After processing, ensure the cache is saved
        self._cache.save()
        return result

    def _process_fetched_url_title(self, url: str | Any, url_title: str | None) -> str:
        url_title = re.sub(r'[\n\t\r]+', ' ', url_title)
        # Replace only two or more consecutive spaces with a single space
        url_title = re.sub(r' {2,}', ' ', url_title)

        if url_title:
            # Put title into cache
            self._cache.put(url, url_title)
        return url_title
