from click_extra import echo
from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComCode

from ..utils import echo_red, echo_yellow


def run_listing(tps: GeoCom) -> None:
    resp_setup = tps.csv.setup_listing()
    if resp_setup.error != GeoComCode.OK:
        echo_red(f"Could not set up job listing ({resp_setup.error.name})")
        return

    resp_list = tps.csv.list()
    if resp_list.error != GeoComCode.OK or resp_list.params is None:
        echo_red(f"Could not start listing ({resp_list.error.name})")
        return

    job, file, _, _, _ = resp_list.params
    if job == "" or file == "":
        echo_yellow("No jobs were found")
        return

    count = 1
    echo(f"{'job name':<50.50s}{'file name':<50.50s}")
    echo(f"{'--------':<50.50s}{'---------':<50.50s}")
    fmt = "{job:<50.50s}{file:<50.50s}"
    echo(
        fmt.format_map(
            {
                "job": job,
                "file": file
            }
        )
    )
    while True:
        resp_list = tps.csv.list()
        if resp_list.error != GeoComCode.OK or resp_list.params is None:
            break

        job, file, _, _, _ = resp_list.params
        echo(
            fmt.format_map(
                {
                    "job": job,
                    "file": file
                }
            )
        )
        count += 1

    echo("-" * 90)
    echo(f"total: {count} files")


def main_list(
    port: str,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False
) -> None:
    with open_serial(
        port=port,
        speed=baud,
        timeout=timeout,
        retry=retry,
        sync_after_timeout=sync_after_timeout
    ) as com:
        tps = GeoCom(com)
        run_listing(tps)
