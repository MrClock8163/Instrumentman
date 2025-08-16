from logging import (
    DEBUG,
    INFO,
    WARNING,
    ERROR,
    CRITICAL,
    NOTSET,
    StreamHandler,
    NullHandler,
    basicConfig,
    Handler,
    LogRecord
)
from sys import stdout, stderr
from logging.handlers import RotatingFileHandler
import os
from typing import Any, Callable, TypeVar
from re import compile
from pathlib import Path

from click_extra import (
    Color,
    echo,
    style,
    option,
    option_group,
    argument,
    Choice,
    IntRange,
    file_path,
    ParamType,
    Context,
    Parameter
)
from cloup.constraints import (
    ErrorFmt,
    constraint,
    mutually_exclusive,
    require_one,
    require_any,
    require_all,
    If,
    AnySet
)


F = TypeVar('F', bound=Callable[..., Any])


EXIT_CODE_DESCRIPTIONS: dict[int, str] = {
    1: "Unknown",
    2: "Keyboard interrupt",
    3: "Missing dependencies",
    4: "Malformed data",
    1100: "Error in target point CSV",
    1101: "Duplicate targets between CSV and existing JSON",
    1102: "Error while opening point CSV",
    1103: "Target CSV file does not exist",
    1200: "Unknown measurement order"
}


def com_port_argument() -> Callable[[F], F]:
    return argument(
        "port",
        help=(
            "Serial port that the instrument is connected to (must be a valid "
            "identifier like COM1 or /dev/usbtty0)"
        ),
        type=str
    )


def com_timeout_option(
    default: int = 15
) -> Callable[[F], F]:
    return option(
        "-t",
        "--timeout",
        help="Serial timeout",
        type=IntRange(min=0),
        default=default
    )


def com_baud_option(
    default: int = 9600
) -> Callable[[F], F]:
    return option(
        "-b",
        "--baud",
        help="Serial speed",
        type=Choice(
            [
                "1200",
                "2400",
                "4800",
                "9600",
                "19200",
                "38400",
                "56000",
                "57600",
                "115200",
                "230400",
                "921600"
            ]
        ),
        callback=lambda ctx, param, value: int(value),
        default=str(default)
    )


def com_option_group() -> Callable[[F], F]:
    return option_group(
        "Connection options",
        com_baud_option(),
        com_timeout_option(),
        option(
            "-r",
            "--retry",
            help="Number of connection retry attempts",
            type=IntRange(min=0, max=10),
            default=1
        ),
        option(
            "--sync-after-timeout",
            help="Attempt to synchronize message que after a timeout",
            is_flag=True
        )
    )


def logging_option_group() -> Callable[[F], F]:
    return option_group(
        "Logging options",
        option(
            "--protocol",
            help=(
                "Log debug level messages and above, "
                "including protocol messages"
            ),
            is_flag=True
        ),
        option(
            "--debug",
            help="Log debug level messages and above",
            is_flag=True
        ),
        option(
            "--info",
            help="Log information level messages and above",
            is_flag=True
        ),
        option(
            "--warning",
            help="Log warning level messages and above",
            is_flag=True
        ),
        option(
            "--error",
            help="Log error level messages and above",
            is_flag=True
        ),
        option(
            "--critical",
            help="Log critical error level messages",
            is_flag=True
        ),
        option(
            "--file",
            help="Log to file",
            type=file_path(readable=False)
        ),
        option(
            "--stdout",
            help="Log to standard output",
            is_flag=True
        ),
        option(
            "--stderr",
            help="Log to standard error",
            is_flag=True
        ),
        option(
            "--format",
            help=(
                "Logging format string (as accepted by the `logging` package "
                "in '{' style)"
            ),
            type=str,
            default="{asctime} <{name}> [{levelname}] {message}"
        ),
        option(
            "--dateformat",
            help="Date-time format spec (as accepted by `strftime`)",
            type=str,
            default="%Y-%m-%d %H:%M:%S"
        ),
        option(
            "--rotate",
            help=(
                "Number of backup log files to rotate, and maximum size "
                "(in bytes) of a log file before rotation"
            ),
            type=(IntRange(1), IntRange(1))
        )
    )


def logging_levels_constraint() -> Callable[[F], F]:
    return constraint(
        mutually_exclusive,
        ["protocol", "debug", "info", "warning", "error", "critical"]
    )


def logging_output_constraint() -> Callable[[F], F]:
    return constraint(
        If(AnySet("file", "stdout", "stderr"), require_one),
        ["protocol", "debug", "info", "warning", "error", "critical"]
    )


def logging_target_constraint() -> Callable[[F], F]:
    return constraint(
        If(
            AnySet(
                "protocol",
                "debug",
                "info",
                "warning",
                "error",
                "critical"
            ),
            require_any
        ),
        ["file", "stdout", "stderr"]
    )


def logging_rotation_constraint() -> Callable[[F], F]:
    return constraint(
        If("rotate", require_all).rephrased(
            help="required if --rotate is set",
            error=(
                "when --rotate is set, the following parameter must also be "
                f"set:\n{ErrorFmt.param_list}"
            )
        ),
        ["file"]
    )


def echo_color(
    message: Any,
    color: str,
    newline: bool = True,
    error: bool = False
) -> None:
    echo(
        style(
            message,
            color
        ),
        nl=newline,
        err=error
    )


def echo_yellow(
    message: Any,
    newline: bool = True,
    error: bool = False
) -> None:
    echo_color(message, Color.yellow, newline, error)


def echo_green(
    message: Any,
    newline: bool = True,
    error: bool = False
) -> None:
    echo_color(message, Color.green, newline, error)


def echo_red(
    message: Any,
    newline: bool = True,
    error: bool = False
) -> None:
    echo_color(message, Color.red, newline, error)


class Angle(ParamType):
    name = "angle"
    _PAT = compile(r"^-?[0-9]{1,3}(-[0-9]{1,2}){0,2}(\.\d+)?$")

    def convert(
        self,
        value: str,
        param: Parameter | None,
        ctx: Context | None
    ) -> str:
        if not self._PAT.match(value):
            self.fail(
                f"{value} is not a valid angle "
                "(valid format is [-][DD]D-MM-SS[.SSSS...])",
                param,
                ctx
            )
            return

        return value


def make_directory(filepath: str) -> None:
    dirname = os.path.dirname(filepath)
    if dirname == "":
        return

    os.makedirs(dirname, exist_ok=True)


class ProtocolFilter:
    def filter(self, record: LogRecord) -> bool:
        message = record.getMessage()
        if (
            message.startswith("GeoComResponse")
            or message.startswith("GsiOnlineResponse")
        ):
            return False

        return True


def configure_logging(
    protocol: bool = False,
    debug: bool = False,
    info: bool = False,
    warning: bool = False,
    error: bool = False,
    critical: bool = False,
    to_path: Path | None = None,
    to_stdout: bool = False,
    to_stderr: bool = False,
    format: str = "{message}",
    dateformat: str = "%Y-%m-%d %H:%M:%S",
    rotate: tuple[int, int] | None = None
) -> None:
    level = NOTSET
    if debug or protocol:
        level = DEBUG
    elif info:
        level = INFO
    elif warning:
        level = WARNING
    elif error:
        level = ERROR
    elif critical:
        level = CRITICAL

    handlers: list[Handler] = []
    if to_path is not None:
        max_size = 0
        backups = 0
        if rotate is not None:
            backups, max_size = rotate

        handlers.append(
            RotatingFileHandler(
                to_path,
                encoding="utf8",
                maxBytes=max_size,
                backupCount=backups
            )
        )

    if to_stdout:
        handlers.append(StreamHandler(stdout))

    if to_stderr:
        handlers.append(StreamHandler(stderr))

    if not protocol:
        flt = ProtocolFilter()
        for h in handlers:
            h.addFilter(flt)

    if len(handlers) == 0:
        handlers = [NullHandler()]

    basicConfig(
        format=format,
        datefmt=dateformat,
        style="{",
        level=level,
        handlers=handlers
    )
