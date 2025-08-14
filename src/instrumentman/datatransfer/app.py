from io import BufferedWriter, TextIOWrapper
from logging import getLogger

from serial import SerialTimeoutException
from rich.progress import Progress, TextColumn
from click_extra import echo
from geocompy.communication import open_serial

from ..utils import echo_green, echo_red, echo_yellow


def main_download(
    port: str,
    baud: int = 9600,
    timeout: int = 2,
    output: BufferedWriter | None = None,
    eof: str = "",
    autoclose: bool = True,
    include_eof: bool = False
) -> None:
    eof_bytes = eof.encode("ascii")
    logger = getLogger("iman.data.download")
    with open_serial(
        port,
        speed=baud,
        timeout=timeout,
        logger=logger.getChild("com")
    ) as com:
        eol_bytes = com.eombytes
        started = False
        logger.info("Starting data download")
        logger.debug("Waiting for first line...")
        while True:
            try:
                data = com.receive_binary()
                if not started:
                    started = True
                    logger.debug("Received first line...")

                if data == eof_bytes and autoclose and not include_eof:
                    echo_green("Download finished (end-of-file)")
                    logger.info("Download finished (end-of-file)")
                    break

                echo(data.decode("ascii", "replace"))
                if output is not None:
                    output.write(data + eol_bytes)

                if data == eof_bytes and autoclose:
                    echo_green("Download finished (end-of-file)")
                    logger.info("Download finished (end-of-file)")
                    break
            except SerialTimeoutException:
                if started and autoclose:
                    echo_green("Download finished (timeout)")
                    logger.info("Download finished (timeout)")
                    break
            except KeyboardInterrupt:
                echo_yellow("Download stopped manually")
                logger.info("Download stopped manually")
                break
            except Exception as e:
                echo_red(f"Download interrupted by error ({e})")
                logger.exception("Download interrupted by error")
                break


def main_upload(
    port: str,
    file: TextIOWrapper,
    baud: int = 1200,
    timeout: int = 15,
    skip: int = 0
) -> None:
    logger = getLogger("iman.data.upload")
    with open_serial(
        port,
        speed=baud,
        timeout=timeout,
        logger=logger.getChild("com")
    ) as com:
        try:
            logger.info("Starting data upload")
            logger.debug(f"Skipping {skip} line(s)")
            for _ in range(skip):
                next(file)

            with Progress(
                *Progress.get_default_columns(),
                TextColumn("{task.completed} line(s)")
            ) as progress:
                for line in progress.track(file, description="Uploading..."):
                    com.send(line)

        except KeyboardInterrupt:
            echo_yellow("Upload cancelled")
            logger.info("Upload cancelled by user")
        except Exception as e:
            echo_red(f"Upload interrupted by error ({e})")
            logger.exception("Upload interrupted by error")
        else:
            echo_green("Upload finished")
            logger.info("Upload finished")
