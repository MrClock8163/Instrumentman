from io import BufferedWriter
from os import linesep

from serial import SerialTimeoutException
from click_extra import echo
from geocompy.communication import open_serial

from ..utils import echo_green, echo_red, echo_yellow


def main_download(
    port: str,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False,
    output: BufferedWriter | None = None,
    eof: str = ""
) -> None:
    eof_bytes = eof.encode("ascii")
    eol_bytes = linesep.encode("ascii")
    with open_serial(
        port,
        speed=baud,
        timeout=2,
        retry=retry,
        sync_after_timeout=sync_after_timeout
    ) as com:
        while True:
            try:
                data = com.receive_binary()
                echo(data.decode("ascii", "replace"))
                if output is not None:
                    output.write(data + eol_bytes)

                if data == eof_bytes:
                    break
            except SerialTimeoutException:
                pass
            except KeyboardInterrupt:
                echo_yellow("Transfer stopped manually")
                return
            except Exception as e:
                echo_red(f"Transfer interrupted by error ({e})")
                return

        echo_green("Transfer finished")
