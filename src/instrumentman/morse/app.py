from time import sleep
from typing import Callable, Any

from click_extra import progressbar

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
    for word in message.lower().split(" "):
        w: list[str] = []
        for letter in word:
            w.append("|".join(MORSE_TABLE.get(letter, "")))

        words.append("_".join(w))

    return " ".join(words)


def relay_message(
    beepstart: Callable[[], Any],
    beepstop: Callable[[], Any],
    message: str,
    unittime: float
) -> None:
    encoded = encode_message(message)
    with progressbar(
        encoded,
        label="Relaying message",
        show_eta=False
    ) as stream:
        for char in stream:
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
    if not ignore_non_ascii:
        try:
            message.casefold().encode("ascii")
        except UnicodeEncodeError:
            echo_red("The message contains non-ASCII characters.")
            exit(1)

    with open_serial(
        port,
        speed=baud,
        timeout=timeout,
        retry=retry,
        sync_after_timeout=sync_after_timeout
    ) as com:
        tps = GeoCom(com)
        beepstart = tps.bmm.beep_start
        beepstop = tps.bmm.beep_stop
        match compatibility.lower():
            case "tps1000":
                beepstart = tps.bmm.beep_on
                beepstop = tps.bmm.beep_off
            case "none":
                pass

        relay_message(
            lambda: beepstart(intensity),
            beepstop,
            message,
            unittime * 1e-3
        )
        echo_green("Message complete.")
