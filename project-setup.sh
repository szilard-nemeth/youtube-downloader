#!/usr/bin/env bash

function youtube-downloader-videos {
    PROJECT_REPO_ROOT="$HOME/development/my-repos/youtube-downloader/"
    # cd $PROJECT_REPO_ROOT && poetry run python youtube_downloader/cli/cli.py "$@"
    cd $PROJECT_REPO_ROOT && poetry run youtube-downloader-videos "$@"
}

# Export the function so it's inherited by subshells.
export -f youtube-downloader