import logging
import os
import pathlib
from copy import copy
from logging.handlers import TimedRotatingFileHandler
from os.path import expanduser
from typing import List

from pythoncommons.constants import ExecutionMode
from pythoncommons.logging_setup import DEFAULT_FORMAT, SimpleLoggingSetupConfig, SimpleLoggingSetup
from pythoncommons.project_utils import ProjectRootDeterminationStrategy, ProjectUtils

from youtube_downloader.constants import PROJECT_NAME
import logging
LOG = logging.getLogger(__name__)


class LoggingUtils:
    INITIALIZED = False

    @classmethod
    def init_with_basic_config(cls,
                               debug: bool = False,
                               temporary_init: bool = False) -> int:
        # If already initialized, return root logger's log level
        if cls.INITIALIZED:
            return logging.getLogger().level
        # If temporary init, do not save as INITIALIZED
        if temporary_init:
            return cls._init_with_basic_config(debug=debug)

        # Otherwise init and save as INITIALIZED
        level = cls._init_with_basic_config(debug=debug)
        cls.INITIALIZED = True
        return level

    @classmethod
    def _init_with_basic_config(cls,
                                debug: bool = False):
        level = logging.DEBUG if debug else logging.INFO
        fmt = DEFAULT_FORMAT
        logging.basicConfig(format=fmt, level=level)
        return level

    @staticmethod
    def _create_file_handler(log_file_dir, level: int, fname: str):
        log_file_path = os.path.join(log_file_dir, f"{fname}.log")
        fh = TimedRotatingFileHandler(log_file_path, when="midnight")
        fh.suffix = "%Y_%m_%d.log"
        fh.setLevel(level)
        return fh

    @staticmethod
    def configure_file_logging(ctx, level, session_dir):
        root_logger = logging.getLogger()
        handlers = copy(root_logger.handlers)
        file_handler = LoggingUtils._create_file_handler(session_dir, level, fname="trello-session")
        file_handler.formatter = None
        LOG.info("Logging to file: %s", file_handler.baseFilename)
        handlers.append(file_handler)

        fmt = DEFAULT_FORMAT
        if ctx.dry_run:
            fmt = f"[DRY-RUN] {fmt}"
        logging.basicConfig(force=True, format=fmt, level=level, handlers=handlers)

    @staticmethod
    def project_setup(ctx,
                      execution_mode: ExecutionMode = ExecutionMode.PRODUCTION,
                      add_console_handler=False,
                      sanity_check_handlers=False):
        strategy = None
        if execution_mode == ExecutionMode.PRODUCTION:
            strategy = ProjectRootDeterminationStrategy.SYS_PATH
        elif execution_mode == ExecutionMode.TEST:
            strategy = ProjectRootDeterminationStrategy.SYS_PATH
        if not strategy:
            raise ValueError("Unknown project root determination strategy!")
        LOG.info("Project root determination strategy is: %s", strategy)
        ProjectUtils.project_root_determine_strategy = strategy
        ProjectUtils.FORCE_SITE_PACKAGES_IN_PATH_NAME = False
        _ = ProjectUtils.get_output_basedir(PROJECT_NAME, basedir=expanduser("~"))

        fmt = DEFAULT_FORMAT
        if ctx.dry_run:
            fmt = f"[DRY-RUN] {fmt}"
        logging_config: SimpleLoggingSetupConfig = SimpleLoggingSetup.init_logger(
            project_name=PROJECT_NAME,
            logger_name_prefix=PROJECT_NAME,
            execution_mode=ExecutionMode.TEST,
            console_debug=True,
            postfix=None,
            verbose_git_log=True,
            format_str=fmt,
            add_console_handler=add_console_handler,
            sanity_check_number_of_handlers=sanity_check_handlers
        )
        LOG.info("Logging to files: %s", logging_config.log_file_paths)
        ctx.log_files = list(logging_config.log_file_paths.values())

    @staticmethod
    def remove_console_handler(logger):
        filtered_handlers = list(
            filter(lambda h: isinstance(h, logging.StreamHandler) and h.stream in (sys.stdout, sys.stderr),
                   logger.handlers))

        for handler in filtered_handlers:
            logger.removeHandler(handler)


class FileUtils:
    @staticmethod
    def load_urls(file_path: str) -> List[str]:
        p = pathlib.Path(file_path)
        if not p.exists():
            raise FileNotFoundError(f"URLs file not found: {file_path}")
        with p.open("r", encoding="utf-8") as fh:
            lines = [l.strip() for l in fh.readlines() if l.strip() and not l.strip().startswith("#")]
        return lines