from logging import Logger, getLogger

from rich.live import Live
from rich.table import Table, Column
from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComCode

from ..utils import echo_red, echo_yellow


def run_listing(
    tps: GeoCom,
    logger: Logger
) -> None:
    logger.info("Starting job listing")
    resp_setup = tps.csv.setup_listing()
    if resp_setup.error != GeoComCode.OK:
        echo_red("Could not set up listing")
        logger.critical(
            f"Could not set up listing ({resp_setup})"
        )
        return

    resp_list = tps.csv.list()
    if resp_list.error != GeoComCode.OK or resp_list.params is None:
        echo_red("Could not start listing")
        logger.critical(f"Could not start listing ({resp_list})")
        return

    job, file, _, _, _ = resp_list.params
    if job == "" or file == "":
        echo_yellow("No jobs were found")
        logger.info("No jobs were found")
        return

    count = 1
    col_file = Column("File Name", footer="1")
    table = Table(
        Column("Job Name", footer="Total:"),
        col_file
    )
    table.add_row(job, file)
    with Live(table):
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


def main_list(
    port: str,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False
) -> None:
    logger = getLogger("iman.jobs.list")
    with open_serial(
        port=port,
        speed=baud,
        timeout=timeout,
        retry=retry,
        sync_after_timeout=sync_after_timeout,
        logger=logger.getChild("com")
    ) as com:
        tps = GeoCom(com, logger.getChild("instrument"))
        try:
            run_listing(tps, logger)
        finally:
            tps.csv.abort_listing()
