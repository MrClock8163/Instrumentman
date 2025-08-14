from time import sleep
from typing import Callable, Any
from logging import Logger, getLogger

from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn

from geocompy.geo import GeoCom
from geocompy.communication import open_serial

from ..utils import (
    echo_red,
    echo_green
)


MORSE_TABLE = {
    "a": ".-",
    "b": "-...",
    "c": "-.-.",
    "d": "-..",
    "e": ".",
    "f": "..-.",
    "g": "--.",
    "h": "....",
    "i": "..",
    "j": ".---",
    "k": "-.-",
    "l": ".-..",
    "m": "--",
    "n": "-.",
    "o": "---",
    "p": ".--.",
    "q": "--.-",
    "r": ".-.",
    "s": "...",
    "t": "-",
    "u": "..-",
    "v": "...-",
    "w": ".--",
    "x": "-..-",
    "y": "-.--",
    "z": "--..",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    "0": "-----",
    "&": ".-...",
    "'": ".----.",
    "@": ".--.-.",
    "(": "-.--.",
    ")": "-.--.-",
    ":": "---...",
    ",": "--..--",
    "=": "-...-",
    "!": "-.-.--",
    ".": ".-.-.-",
    "-": "-....-",
    "%": "------..-.-----",
    "+": ".-.-.",
    "\"": ".-..-.",
    "?": "..--..",
    "/": "-..-.",
    "\n": ".-.-"
}


def encode_message(
    message: str
) -> str:
    words: list[str] = []
    for word in message.casefold().split(" "):
        w: list[str] = []
        for letter in word:
            w.append("|".join(MORSE_TABLE.get(letter, "")))

        words.append("_".join(w))

    return " ".join(words)


def relay_message(
    logger: Logger,
    beepstart: Callable[[], Any],
    beepstop: Callable[[], Any],
    message: str,
    unittime: float
) -> None:
    logger.info(f"Starting morse message: '{message}'")
    encoded = encode_message(message)
    logger.info("Message encoded")
    logger.info("Relaying message...")
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn()
    ) as progress:
        for char in progress.track(encoded, description="Relaying message"):
            match char:
                case ".":
                    beepstart()
                    sleep(unittime)
                    beepstop()
                case "-":
                    beepstart()
                    sleep(3 * unittime)
                    beepstop()
                case "|":
                    sleep(unittime)
                case "_":
                    sleep(3 * unittime)
                case " ":
                    sleep(7 * unittime)
                case _:
                    raise ValueError(
                        f"Invalid morse stream character: '{char}'"
                    )

    echo_green("Message complete")
    logger.info("Message complete")


def main(
    port: str,
    message: str,
    intensity: int = 100,
    ignore_non_ascii: bool = False,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False,
    unittime: int = 50,
    compatibility: str = "none",
) -> None:
    logger = getLogger("iman.morse")
    if not ignore_non_ascii:
        try:
            message.casefold().encode("ascii")
        except UnicodeEncodeError:
            echo_red("The message contains non-ASCII characters.")
            logger.critical("Message contains non-ASCII characters.")
            exit(1)

    with open_serial(
        port,
        speed=baud,
        timeout=timeout,
        retry=retry,
        sync_after_timeout=sync_after_timeout,
        logger=logger.getChild("com")
    ) as com:
        tps = GeoCom(com, logger.getChild("instrument"))
        beepstart = tps.bmm.beep_start
        beepstop = tps.bmm.beep_stop
        match compatibility.lower():
            case "tps1000":
                logger.debug(f"Running with '{compatibility}' compatibility")
                beepstart = tps.bmm.beep_on
                beepstop = tps.bmm.beep_off
            case "none":
                pass

        relay_message(
            logger,
            lambda: beepstart(intensity),
            beepstop,
            message,
            unittime * 1e-3
        )
