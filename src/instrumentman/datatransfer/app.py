from io import BufferedWriter

from serial import SerialTimeoutException
from click_extra import echo
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
                    echo_green("Transfer finished (end-of-file)")
                    return
            except SerialTimeoutException:
                if started and autoclose:
                    echo_green("Transfer finished (timeout)")
                    return
            except KeyboardInterrupt:
                echo_yellow("Transfer stopped manually")
                return
            except Exception as e:
                echo_red(f"Transfer interrupted by error ({e})")
                return
