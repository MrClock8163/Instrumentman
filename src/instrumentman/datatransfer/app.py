from io import BufferedWriter, TextIOWrapper
from logging import getLogger

from rich.progress import Progress, TextColumn, BarColumn, TimeElapsedColumn
from geocompy.communication import open_serial

from ..utils import (
    print_success,
    print_error,
    print_warning,
    print_plain,
    console,
    theme_progress_interrupted,
    theme_progress_error
)


def main_download(
    port: str,
    baud: int = 9600,
    timeout: int = 2,
    output: BufferedWriter | None = None,
    eof: str | None = None,
    autoclose: bool = True,
    include_eof: bool = False
) -> None:
    eof_bytes: bytes | None = None
    if eof is not None:
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
        logger.debug("Waiting for first line")
        with Progress(
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed} line(s)"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            task = progress.add_task("Waiting for data", total=None)

            lines = 0
            while True:
                try:
                    data = com.receive_binary()
                    if not started:
                        started = True
                        logger.debug("Received first line")
                        progress.update(task, description="Receiving data")

                    if (
                        eof_bytes is not None
                        and data == eof_bytes
                        and autoclose
                        and not include_eof
                    ):
                        logger.info("Download finished (end-of-file)")
                        print_success("Download reached end-of-file")

                        progress.update(
                            task,
                            total=lines
                        )
                        break

                    print_plain(data.decode("ascii", "replace"))
                    lines += 1
                    progress.update(task, completed=lines)
                    if output is not None:
                        output.write(data + eol_bytes)

                    if (
                        eof_bytes is not None
                        and data == eof_bytes
                        and autoclose
                    ):
                        logger.info("Download finished (end-of-file)")
                        print_success("Download reached end-of-file")

                        progress.update(
                            task,
                            total=lines
                        )
                        break
                except TimeoutError:
                    if started and autoclose:
                        logger.info("Download finished (timeout)")
                        print_success("Download finished due to timeout")

                        progress.update(
                            task,
                            total=lines
                        )
                        break
                except KeyboardInterrupt:
                    logger.info("Download stopped manually")
                    print_warning("Manually interrupted")
                    console.push_theme(theme_progress_interrupted)
                    progress.update(
                        task,
                        refresh=True
                    )
                    break
                except Exception as e:
                    print_error(e)
                    console.push_theme(theme_progress_error)
                    progress.update(
                        task,
                        refresh=True
                    )
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
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("{task.completed} line(s)"),
                TimeElapsedColumn(),
                console=console
            ) as progress:
                lines = 0
                task = progress.add_task("Uploading", total=None)
                for line in file:
                    lines += 1
                    com.send(line)
                    progress.update(task, completed=lines)

                progress.update(task, total=lines)

        except KeyboardInterrupt:
            print_warning("Upload cancelled")
            logger.info("Upload cancelled by user")
        except Exception as e:
            print_error(f"Upload interrupted by error ({e})")
            logger.exception("Upload interrupted by error")
