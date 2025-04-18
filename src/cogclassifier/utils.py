from __future__ import annotations

import logging
import os
import signal
import sys
import time
from functools import partial, wraps
from pathlib import Path
from typing import Callable

import requests


def ftp_download(
    url: str,
    outdir: str | Path,
    overwrite: bool = False,
) -> Path:
    """Download file from FTP site

    Parameters
    ----------
    url : str
        FTP site url for download
    outdir : str | Path
        Output directory
    overwrite : bool, optional
        Overwrite or not

    Returns
    -------
    download_file : Path
        Download file path
    """
    os.makedirs(outdir, exist_ok=True)
    download_file = Path(outdir) / Path(url).name
    logger = logging.getLogger(__name__)
    logger.info(f"Download {url}")

    if download_file.exists() and not overwrite:
        logger.info(f"=> Already file exists {download_file}")
        return download_file
    try:
        res = requests.get(url, stream=True)
        with open(download_file, "wb") as f:
            f.write(res.content)
        logger.info(f"=> Successfully downloaded {download_file}")
        return download_file
    except requests.exceptions.ConnectionError:
        logger.exception("Failed to download file. Please check network connection.")
        raise


def logging_timeit(
    func: Callable | None = None,
    /,
    *,
    show_func_name: bool = False,
    debug: bool = False,
):
    """Elapsed time logging decorator

    e.g. `Done (elapsed time: 82.3[s]) [module.function]`

    Parameters
    ----------
    func : Callable | None, optional
        Target function
    show_func_name : bool, optional
        If True, show elapsed time message with `module.function` definition
    debug : bool, optional
        If True, use `logger.debug` (By default `logger.info`)
    """
    if func is None:
        return partial(logging_timeit, show_func_name=show_func_name, debug=debug)

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        logger = logging.getLogger(__name__)
        msg = f"Done (elapsed time: {elapsed_time:.2f}[s])"
        if show_func_name:
            msg = f"{msg} [{func.__module__}.{func.__name__}]"
        logger_func = logger.debug if debug else logger.info
        logger_func(msg)
        return result

    return wrapper


def exit_handler(func):
    """Exit handling decorator on exception

    The main purpose is logging on keyboard interrupt exception
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            logger = logging.getLogger(__name__)
            logger.exception("Keyboard Interrupt")
            sys.exit(signal.SIGINT)
        except Exception:
            sys.exit(1)

    return wrapper
