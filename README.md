# youtube-downloader


## Example commands (standard yt-dlp)

List formats for a video: 
```shell
yt-dlp -F "https://youtu.be/ZRfiLKxBl7c"
yt-dlp --cookies-from-browser chrome -F "https://youtu.be/ZRfiLKxBl7c"
```

Playing with various formats
```shell
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4" "https://youtu.be/ZRfiLKxBl7c"
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best" "https://youtu.be/ZRfiLKxBl7c"
```

Use browser cookies from Chrome
```shell
yt-dlp --cookies-from-browser chrome -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4" "https://youtu.be/ZRfiLKxBl7c"
yt-dlp --cookies-from-browser chrome -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best" "https://youtu.be/ZRfiLKxBl7c"
```

## Example commands (poetry)

### Download mp3 files
```shell
poetry run youtube-downloader-audios --no-browser-cookies /Users/szilardnemeth/Downloads/youtube-download-mp3.txt
```

### Download videos
```shell
poetry run youtube-downloader-videos --no-browser-cookies /Users/szilardnemeth/Downloads/youtube-download.txt
poetry run youtube-downloader-videos /Users/szilardnemeth/Downloads/youtube-download.txt
poetry run youtube-downloader-videos --no-browser-cookies /Users/szilardnemeth/Downloads/youtube-download-temp.txt
```

### Get video titles
```shell
poetry run youtube-downloader-get-titles /Users/szilardnemeth/Downloads/youtube-download.txt
poetry run youtube-downloader-get-titles --force-download /Users/szilardnemeth/Downloads/youtube-download.txt
poetry run youtube-downloader-get-titles --force-download --no-browser-cookies /Users/szilardnemeth/Downloads/youtube-download.txt
```

# Troubleshooting

## Issues found

### JS Challenge solver - Deno cannot download npm dependencies
JS challenges are solved by a JS Challenge Provider.
`deno` is not installed correctly for some reason.
This can only be seen if trace logging is enabled.
Add this to the dl_opts config dictionary: 
```python
'extractor_args': {
    'youtube': {  # or the specific extractor name you need
        'jsc_trace': ['true'] # it's weird but it expects a list and lowercase boolean str
    }
}
```

Also, the problem is that by default yt-dlp can't download external JS components.
https://github.com/yt-dlp/yt-dlp/wiki/EJS#notes
> Supports downloading EJS script dependencies from npm (--remote-components ejs:npm).



```
import sys; print('Python %s on %s' % (sys.version, sys.platform))
/Users/szilardnemeth/Library/Caches/pypoetry/virtualenvs/youtube-downloader-ZywhhSFv-py3.12/bin/python -X pycache_prefix=/Users/szilardnemeth/Library/Caches/JetBrains/PyCharm2025.2/cpython-cache /Users/szilardnemeth/Applications/PyCharm.app/Contents/plugins/python-ce/helpers/pydev/pydevd.py --multiprocess --qt-support=auto --client 127.0.0.1 --port 49169 --file /Users/szilardnemeth/development/my-repos/youtube-downloader/youtube_downloader/download_videos_from_file.py /Users/szilardnemeth/Downloads/youtube-download.txt 
Connected to: <socket.socket fd=3, family=2, type=1, proto=0, laddr=('127.0.0.1', 49170), raddr=('127.0.0.1', 49169)>.
Connected to pydev debugger (build 252.27397.106)
=== Downloading 1/103: https://youtu.be/ZRfiLKxBl7c?si=Dy1n5ukI3YRmhVi5 ===
WARNING: Ignoring unsupported remote component(s): e, u, s, g, :, t, h, j, i, b. Supported remote components: ejs:github, ejs:npm.
[debug] Encodings: locale UTF-8, fs utf-8, pref UTF-8, out utf-8 (No ANSI), error utf-8 (No ANSI), screen utf-8 (No ANSI)
[debug] yt-dlp version stable@2025.11.12 from yt-dlp/yt-dlp [335653be8] (pip) API
[debug] params: {'outtmpl': '/Users/szilardnemeth/youtube-downloader-output/yt-dlp/%(playlist_title)s/%(title)s.%(ext)s', 'ignoreerrors': False, 'noplaylist': False, 'continuedl': True, 'retries': 10, 'concurrent_fragment_downloads': 5, 'nooverwrites': True, 'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4', 'progress_hooks': [<function progress_hook at 0x105498b80>], 'quiet': False, 'verbose': True, 'remote_components': set(), 'force_no_merge': False, 'merge_output_format': 'mp4', 'compat_opts': {'force-merge'}, 'postprocessor_hooks': [<function post_hook at 0x10577ede0>, <function verify_output at 0x10577f060>], 'extractor_args': {'youtube': {'jsc_trace': ['true']}}, 'cookiesfrombrowser': ('chrome',), 'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}], 'nopart': False, 'js_runtimes': {'deno': {}}, 'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36', 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-us,en;q=0.5', 'Sec-Fetch-Mode': 'navigate'}}
[debug] Compatibility options: force-merge
[debug] Python 3.12.3 (CPython arm64 64bit) - macOS-15.6-arm64-arm-64bit (OpenSSL 3.6.0 1 Oct 2025)
[debug] exe versions: ffmpeg 8.0.1 (setts), ffprobe 8.0.1
[debug] Optional libraries: certifi-2025.11.12, requests-2.32.5, sqlite3-3.51.1, urllib3-2.6.0
[debug] JS runtimes: deno-2.5.6
[debug] Proxy map: {}
Extracting cookies from chrome
[debug] Extracting cookies from: "/Users/szilardnemeth/Library/Application Support/Google/Chrome/Default/Cookies"
[debug] using find-generic-password to obtain password from OSX keychain
Extracted 2774 cookies from chrome
[debug] cookie version breakdown: {'v10': 3373, 'other': 0, 'unencrypted': 0}
[debug] Request Handlers: urllib, requests
[debug] Plugin directories: none
[debug] Loaded 1844 extractors
[debug] [youtube] Found YouTube account cookies
[debug] [youtube] [pot] PO Token Providers: none
[debug] [youtube] [pot] PO Token Cache Providers: memory
[debug] [youtube] [pot] PO Token Cache Spec Providers: webpo
[debug] [youtube] [jsc] JS Challenge Providers: bun (unavailable), deno, node (unavailable), quickjs (unavailable)
[debug] [youtube] [jsc] TRACE: Registered 4 JS Challenge provider preferences
[youtube] Extracting URL: https://youtu.be/ZRfiLKxBl7c?si=Dy1n5ukI3YRmhVi5
[youtube] ZRfiLKxBl7c: Downloading webpage
[debug] [youtube] Detected YouTube Premium subscription
[youtube] ZRfiLKxBl7c: Downloading tv downgraded player API JSON
[youtube] ZRfiLKxBl7c: Downloading web creator player API JSON
[debug] [youtube] [jsc] TRACE: JS Challenge Providers: bun (unavailable), deno, node (unavailable), quickjs (unavailable)
[debug] [youtube] [jsc] TRACE: JS Challenge Provider preferences for this request: bun=800, deno=1000, node=900, quickjs=850
[debug] [youtube] [jsc] TRACE: Attempting to solve 1 challenges using "deno" provider
[youtube] ZRfiLKxBl7c: Downloading player 4e11051b-main
[youtube] [jsc:deno] Solving JS challenges using deno
[debug] [youtube] [jsc:deno] Checking if npm packages are cached
[debug] [youtube] [jsc:deno] Running deno: deno run --ext=js --no-code-cache --no-prompt --no-remote --no-lock --node-modules-dir=none --no-config --cached-only -
[debug] [youtube] [jsc:deno] TRACE: Deno npm packages not cached: Error running deno process (returncode: 1): error: Uncaught (in promise) TypeError: Failed loading https://registry.npmjs.org/meriyah for package "meriyah"
    0: npm package not found in cache: "meriyah", --cached-only is specified.
  meriyah: await import('npm:meriyah@6.1.4'),
           ^
    at async file:///Users/szilardnemeth/development/my-repos/youtube-downloader/youtube_downloader/$deno$stdin.js:6:12
[debug] [youtube] [jsc:deno] Checking if npm packages are cached
[debug] [youtube] [jsc:deno] Running deno: deno run --ext=js --no-code-cache --no-prompt --no-remote --no-lock --node-modules-dir=none --no-config --cached-only -
[debug] [youtube] [jsc:deno] TRACE: Deno npm packages not cached: Error running deno process (returncode: 1): error: Uncaught (in promise) TypeError: Failed loading https://registry.npmjs.org/meriyah for package "meriyah"
    0: npm package not found in cache: "meriyah", --cached-only is specified.
  meriyah: await import('npm:meriyah@6.1.4'),
           ^
    at async file:///Users/szilardnemeth/development/my-repos/youtube-downloader/youtube_downloader/$deno$stdin.js:6:12
[debug] [youtube] [jsc:deno] Checking if npm packages are cached
[debug] [youtube] [jsc:deno] Running deno: deno run --ext=js --no-code-cache --no-prompt --no-remote --no-lock --node-modules-dir=none --no-config --cached-only -
[debug] [youtube] [jsc:deno] TRACE: Deno npm packages not cached: Error running deno process (returncode: 1): error: Uncaught (in promise) TypeError: Failed loading https://registry.npmjs.org/meriyah for package "meriyah"
    0: npm package not found in cache: "meriyah", --cached-only is specified.
  meriyah: await import('npm:meriyah@6.1.4'),
           ^
    at async file:///Users/szilardnemeth/development/my-repos/youtube-downloader/youtube_downloader/$deno$stdin.js:6:12
[debug] [youtube] [jsc:deno] Checking if npm packages are cached
[debug] [youtube] [jsc:deno] Running deno: deno run --ext=js --no-code-cache --no-prompt --no-remote --no-lock --node-modules-dir=none --no-config --cached-only -
[debug] [youtube] [jsc:deno] TRACE: Deno npm packages not cached: Error running deno process (returncode: 1): error: Uncaught (in promise) TypeError: Failed loading https://registry.npmjs.org/meriyah for package "meriyah"
    0: npm package not found in cache: "meriyah", --cached-only is specified.
  meriyah: await import('npm:meriyah@6.1.4'),
           ^
    at async file:///Users/szilardnemeth/development/my-repos/youtube-downloader/youtube_downloader/$deno$stdin.js:6:12
[debug] [youtube] [jsc] TRACE: JS Challenge Provider "deno" rejected this request, trying next available provider. Reason: No usable challenge solver lib script available

```