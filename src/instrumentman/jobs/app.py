from logging import Logger, getLogger

from rich.live import Live
from rich.table import Table, Column
from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComCode
from geocompy.geo.gcdata import Device

from ..utils import print_error, print_warning, console


def run_listing(
    tps: GeoCom,
    device: Device,
    logger: Logger
) -> None:
    logger.info("Starting job listing")
    resp_setup = tps.csv.setup_listing(device)
    if resp_setup.error != GeoComCode.OK:
        print_error("Could not set up listing")
        logger.critical(
            f"Could not set up listing ({resp_setup})"
        )
        return

    resp_list = tps.csv.list()
    if resp_list.error != GeoComCode.OK or resp_list.params is None:
        print_error("Could not start listing")
        logger.critical(f"Could not start listing ({resp_list})")
        return

    job, file, _, _, _ = resp_list.params
    if job == "" or file == "":
        print_warning("No jobs were found")
        logger.info("No jobs were found")
        return

    count = 1
    col_file = Column("File Name", footer="1")
    table = Table(
        Column("Job Name", footer="Total:"),
        col_file
    )
    table.add_row(job, file)
    with Live(table, console=console):
        while True:
            resp_list = tps.csv.list()
            if resp_list.error != GeoComCode.OK or resp_list.params is None:
                break

            job, file, _, _, _ = resp_list.params
            if job == "" or file == "":
                break

            count += 1
            table.add_row(job, file)
            col_file.footer = str(count)

    logger.info("Listing complete")


_DEVICE = {
    "internal": Device.INTERNAL,
    "cf": Device.CFCARD,
    "sd": Device.SDCARD,
    "usb": Device.USB,
    "ram": Device.RAM
}


def main_list(
    port: str,
    baud: int = 9600,
    timeout: int = 15,
    attempts: int = 1,
    sync_after_timeout: bool = False,
    device: str = "internal"
) -> None:
    logger = getLogger("iman.jobs.list")
    with open_serial(
        port=port,
        speed=baud,
        timeout=timeout,
        attempts=attempts,
        sync_after_timeout=sync_after_timeout,
        logger=logger.getChild("com")
    ) as com:
        tps = GeoCom(com, logger=logger.getChild("instrument"))
        try:
            run_listing(tps, _DEVICE[device], logger)
        finally:
            tps.csv.abort_listing()
