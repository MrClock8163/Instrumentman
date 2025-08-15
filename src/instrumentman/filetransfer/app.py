from __future__ import annotations

from io import BufferedWriter
from typing import TypedDict, Callable
import os
from re import compile, IGNORECASE
from logging import getLogger, Logger

from click_extra import echo
from rich.console import Console, RenderableType
from rich.text import Text
from rich.tree import Tree
from rich.table import Table
from rich.filesize import decimal
from rich.progress import Progress, TextColumn
from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComCode
from geocompy.geo.gcdata import File, Device

from ..utils import echo_red, echo_green


_FILE = {
    "image": File.IMAGE,
    "database": File.DATABASE,
    "overview-jpg": File.IMAGES_OVERVIEW_JPG,
    "overview-bmp": File.IMAGES_OVERVIEW_BMP,
    "telescope-jpg": File.IMAGES_TELESCOPIC_JPG,
    "telescope-bmp": File.IMAGES_TELESCOPIC_BMP,
    "scan": File.SCANS,
    "unknown": File.UNKNOWN,
    "last": File.LAST
}


_DEVICE = {
    "internal": Device.INTERNAL,
    "cf": Device.CFCARD,
    "sd": Device.SDCARD,
    "usb": Device.USB,
    "ram": Device.RAM
}


class FileTreeItem(TypedDict):
    name: str
    size: int
    date: str
    children: list[FileTreeItem]


def get_directory_items(
    updater: Callable[[str], None],
    tps: GeoCom,
    logger: Logger,
    device: str,
    directory: str,
    filetype: str,
    depth: int = 0
) -> list[FileTreeItem]:
    if depth == 0:
        return []

    updater(directory)
    resp_setup = tps.ftr.setup_listing(
        _DEVICE[device],
        _FILE[filetype],
        f"{directory}/*"
    )
    if resp_setup.error != GeoComCode.OK:
        logger.error(
            f"Could not set up indexing '{directory}' ({resp_setup})"
        )
        return []
    else:
        logger.debug(f"Indexing '{directory}'")

    resp_list = tps.ftr.list()
    if resp_list.error != GeoComCode.OK or resp_list.params is None:
        logger.error(f"Could not start indexing ({resp_list})")
        tps.ftr.abort_listing()
        return []

    last, name, size, lastmodified = resp_list.params
    if name == "":
        tps.ftr.abort_listing()
        return []

    output: list[FileTreeItem] = []
    output.append(
        {
            "name": name,
            "size": size,
            "date": (
                lastmodified.isoformat(sep=" ")
                if lastmodified is not None
                else ""
            ),
            "children": []
        }
    )
    while not last:
        resp_list = tps.ftr.list(True)
        if resp_list.error != GeoComCode.OK or resp_list.params is None:
            logger.error(f"Stopped indexing due to an error ({resp_list})")
            tps.ftr.abort_listing()
            return []

        last, name, size, lastmodified = resp_list.params
        output.append(
            {
                "name": name,
                "size": size,
                "date": (
                    lastmodified.isoformat(sep=" ")
                    if lastmodified is not None
                    else ""
                ),
                "children": []
            }
        )

    tps.ftr.abort_listing()
    for item in output:
        item["children"] = get_directory_items(
            updater,
            tps,
            logger,
            device,
            f"{directory}/{item['name']}",
            filetype,
            depth=(depth - 1) if depth > 0 else -1
        )

    return output


_RE_DBX = compile(r"(?:.X\d{2})|.xcf", IGNORECASE)
_fmt_dir = ":open_file_folder: [bold blue]{name}[/] [bright_black]({count})"
_fmt_likelydir = ":grey_question: [cyan]{name}"
_fmt_text = ":pencil: [green]{name}"
_fmt_img = ":city_sunset: [bright_magenta]{name}"
_fmt_dbx = ":package: [red]{name}"
_fmt_unkown = ":grey_question: {name}"


def format_tree_item(
    tree: FileTreeItem
) -> RenderableType:

    if len(tree["children"]) > 0:
        name = _fmt_dir.format(
            name=tree["name"],
            count=len(tree["children"])
        )
    else:
        match os.path.splitext(tree["name"])[1].lower():
            case "":
                name = _fmt_likelydir.format_map(tree)
            case ".jpg" | ".jpeg" | ".bmp" | ".dxf" | ".dwg":
                name = _fmt_img.format_map(tree)
            case ".txt" | ".gsi" | ".xml":
                name = _fmt_text.format_map(tree)
            case dbx if _RE_DBX.match(dbx):
                name = _fmt_dbx.format_map(tree)
            case _:
                name = _fmt_unkown.format_map(tree)

    grid = Table.grid(expand=True)
    grid.add_column()
    grid.add_column(justify="right")
    grid.add_row(
        Text.from_markup(name),
        Text(
            f"{decimal(tree['size']):>10.10s}{tree['date']:>25.25s}",
            justify="right"
        )
    )
    return grid


def build_file_tree(
    tree: FileTreeItem,
    branch: Tree | None = None
) -> Tree:
    if branch is None:
        branch = Tree(format_tree_item(tree))

    for item in tree["children"]:
        node = branch.add(format_tree_item(item))
        build_file_tree(item, node)

    return branch


def run_listing_tree(
    tps: GeoCom,
    logger: Logger,
    dev: str,
    directory: str,
    filetype: str | None,
    depth: int = 1
) -> None:
    filetype = filetype or "unknown"
    console = Console(width=120)
    logger.info(
        f"Starting content listing of '{directory}' from '{dev}' device"
    )
    logger.debug(f"Listing options: depth={depth:d}, filetype={filetype}")
    with Progress(
        *Progress.get_default_columns(),
        TextColumn("{task.fields[path]}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task(
            "Indexing directories...",
            total=None,
            path=""
        )
        tree: FileTreeItem = {
            "name": (
                f"{dev.upper()}/{directory}"
                if directory != "/"
                else dev.upper()
            ),
            "size": 0,
            "date": "unknown",
            "children": get_directory_items(
                lambda path: progress.update(task, path=path),
                tps,
                logger,
                dev,
                directory,
                filetype or "unknown",
                -1 if depth == 0 else depth
            )
        }

    logger.info("Listing complete")
    treeview = build_file_tree(tree)
    console.print(treeview)


def run_download(
    tps: GeoCom,
    logger: Logger,
    filename: str,
    file: BufferedWriter,
    device: str = "internal",
    filetype: str = "unknown",
    chunk: int = 225,
    large: bool = False
) -> None:
    setup = tps.ftr.setup_download
    download = tps.ftr.download
    if large:
        setup = tps.ftr.setup_large_download
        download = tps.ftr.download_large

    logger.info(
        f"Starting download of '{filename}' ({filetype} type) "
        f"from '{device}' device"
    )
    logger.debug(f"Download setup: large={str(large)}, chunk={chunk:d}")
    resp_setup = setup(
        filename,
        chunk * 2,  # chunk size is in bytes, but command expects in hex chars
        _DEVICE[device],
        _FILE[filetype]
    )
    if resp_setup.error != GeoComCode.OK or resp_setup.params is None:
        echo_red("Could not set up file download")
        logger.critical(
            f"Could not set up file download ({resp_setup})"
        )
        return

    block_count = resp_setup.params
    logger.info(f"Expected number of chunks: {block_count:d}")

    with Progress() as progress:
        for i in progress.track(range(block_count), description="Downloading"):
            resp_pull = download(i + 1)
            if resp_pull.error != GeoComCode.OK or resp_pull.params is None:
                progress.stop()
                echo_red("An error occured during download")
                logger.critical(
                    f"An error occured during download ({resp_pull})"
                )
                return

            echo(bytes.fromhex(resp_pull.params), file, False)

    logger.info("Download complete")
    echo_green("Download complete")


def main_download(
    port: str,
    filename: str,
    output: BufferedWriter,
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False,
    device: str = "internal",
    filetype: str = "unknown",
    chunk: int = 225,
    large: bool = False
) -> None:
    logger = getLogger("iman.files.download")
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
            run_download(
                tps,
                logger,
                filename,
                output,
                device,
                filetype,
                chunk,
                large
            )
        finally:
            tps.ftr.abort_download()


def main_list(
    port: str,
    directory: str = "/",
    baud: int = 9600,
    timeout: int = 15,
    retry: int = 1,
    sync_after_timeout: bool = False,
    device: str = "internal",
    filetype: str | None = None,
    depth: int = 1
) -> None:
    logger = getLogger("iman.files.list")
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
            run_listing_tree(
                tps,
                logger,
                device,
                directory,
                filetype,
                depth
            )
        finally:
            tps.ftr.abort_listing()
