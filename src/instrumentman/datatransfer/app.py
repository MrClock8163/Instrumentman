from io import BufferedWriter, TextIOWrapper

from serial import SerialTimeoutException
from click_extra import echo, progressbar
from geocompy.communication import open_serial

from ..utils import echo_green, echo_red, echo_yellow


def main_download(
    port: str,
    baud: int = 9600,
    timeout: int = 2,
    output: BufferedWriter | None = None,
    eof: str = "",
    autoclose: bool = True
) -> None:
    eof_bytes = eof.encode("ascii")
    with open_serial(
        port,
        speed=baud,
        timeout=timeout
    ) as com:
        eol_bytes = com.eombytes
        started = False
        while True:
            try:
                data = com.receive_binary()
                started = True
                echo(data.decode("ascii", "replace"))
                if output is not None:
                    output.write(data + eol_bytes)

                if data == eof_bytes and autoclose:
                    echo_green("Download finished (end-of-file)")
                    return
            except SerialTimeoutException:
                if started and autoclose:
                    echo_green("Download finished (timeout)")
                    return
            except KeyboardInterrupt:
                echo_yellow("Download stopped manually")
                return
            except Exception as e:
                echo_red(f"Download interrupted by error ({e})")
                return


def main_upload(
    port: str,
    file: TextIOWrapper,
    baud: int = 1200,
    timeout: int = 15
) -> None:
    with open_serial(
        port,
        speed=baud,
        timeout=timeout
    ) as com:
        try:
            count = 0
            with progressbar(
                file,
                label="Uploading data",
                item_show_func=lambda x: f"{count} line(s)"
            ) as bar:
                for line in bar:
                    com.send(line)
                    count += 1
        except Exception as e:
            echo_red(f"Upload interrupted by error ({e})")
            return

        echo_green("Upload finished")
