from __future__ import annotations

from io import BufferedWriter
from typing import TypedDict
import os
from re import compile, IGNORECASE

from click_extra import echo, progressbar
from rich import print as rprint
from rich.tree import Tree
from rich.filesize import decimal
from geocompy.communication import open_serial
from geocompy.geo import GeoCom
from geocompy.geo.gctypes import GeoComCode
from geocompy.geo.gcdata import File, Device

from ..utils import echo_red, echo_green, echo_yellow


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
    size: int | str
    children: list[FileTreeItem]


def run_listing(
    tps: GeoCom,
    dev: str,
    directory: str,
    filetype: str
) -> None:
    resp_setup = tps.ftr.setup_listing(
        _DEVICE[dev],
        _FILE[filetype],
        directory
    )
    if resp_setup.error != GeoComCode.OK:
        echo_red(f"Could not set up file listing ({resp_setup.error.name})")
        return

    resp_list = tps.ftr.list()
    if resp_list.error != GeoComCode.OK or resp_list.params is None:
        echo_red(f"Could not start listing ({resp_list.error.name})")
        return

    last, name, size, lastmodified = resp_list.params
    if name == "":
        echo_yellow("Directory is empty or path does not exist")
        return

    count = 1
    echo(f"{'file name':<55.55s}{'bytes':>10.10s}{'last modified':>25.25s}")
    echo(f"{'---------':<55.55s}{'-----':>10.10s}{'-------------':>25.25s}")
    fmt = "{name:<55.55s}{size:>10s}{date:>25.25s}"
    echo(
        fmt.format_map(
            {
                "name": name,
                "size": str(size),
                "date": (
                    lastmodified.isoformat(sep=" ")
                    if lastmodified is not None
                    else ""
                )
            }
        )
    )
    while not last:
        resp_list = tps.ftr.list(True)
        if resp_list.error != GeoComCode.OK or resp_list.params is None:
            echo_red(
                f"An error occured during listing ({resp_list.error.name})"
            )
            return

        last, name, size, lastmodified = resp_list.params
        echo(
            fmt.format_map(
                {
                    "name": name,
                    "size": str(size),
                    "date": (
                        lastmodified.isoformat(sep=" ")
                        if lastmodified is not None
                        else ""
                    )
                }
            )
        )
        count += 1

    echo("-" * 90)
    echo(f"total: {count} files")


def get_directory_items(
    tps: GeoCom,
    device: str,
    directory: str,
    depth: int = 0
) -> list[FileTreeItem]:
    if depth == 0:
        return []

    resp_setup = tps.ftr.setup_listing(
        _DEVICE[device],
        File.UNKNOWN,
        f"{directory}/*"
    )
    if resp_setup.error != GeoComCode.OK:
        # tps.ftr.abort_list()
        return []

    resp_list = tps.ftr.list()
    if resp_list.error != GeoComCode.OK or resp_list.params is None:
        tps.ftr.abort_list()
        return []

    last, name, size, lastmodified = resp_list.params
    if name == "":
        tps.ftr.abort_list()
        return []

    output: list[FileTreeItem] = []
    output.append(
        {
            "name": name,
            "size": size,
            "children": []
        }
    )
    count = 1

    while not last:
        resp_list = tps.ftr.list(True)
        if resp_list.error != GeoComCode.OK or resp_list.params is None:
            tps.ftr.abort_list()
            return []

        last, name, size, lastmodified = resp_list.params
        output.append(
            {
                "name": name,
                "size": size,
                "children": []
            }
        )
        count += 1

    tps.ftr.abort_list()
    for item in output:
        item["children"] = get_directory_items(
            tps,
            device,
            f"{directory}/{item['name']}",
            depth=(depth - 1) if depth > 0 else -1
        )

    return output


_RE_DBX = compile(r"(?:.X\d{2})|.xcf", IGNORECASE)


def format_tree_item(
    tree: FileTreeItem
) -> str:
    fmt_dir = ":open_file_folder: [bold blue]{name}"
    fmt_likelydir = ":grey_question: [cyan]{name} [bright_black]({size})"
    fmt_text = ":pencil: [green]{name} [bright_black]({size})"
    fmt_img = ":framed_picture: [bright_magenta]{name} [bright_black]({size})"
    fmt_dbx = ":package: [red]{name} [bright_black]({size})"
    fmt_unkown = ":grey_question: {name} [bright_black]({size})"

    name = tree["name"]
    if isinstance(tree["size"], int):
        tree["size"] = decimal(tree["size"])

    if len(tree["children"]) > 0:
        return fmt_dir.format_map(tree)

    match os.path.splitext(name)[1].lower():
        case "":
            return fmt_likelydir.format_map(tree)
        case ".jpg" | ".jpeg" | ".bmp" | ".dxf" | ".dwg":
            return fmt_img.format_map(tree)
        case ".txt" | ".gsi" | ".xml":
            return fmt_text.format_map(tree)
        case dbx if _RE_DBX.match(dbx):
            return fmt_dbx.format_map(tree)

    return fmt_unkown.format_map(tree)


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
    dev: str,
    directory: str,
    depth: int = 1
) -> None:
    tree: FileTreeItem = {
        "name": directory,
        "size": 0,
        "children": get_directory_items(
            tps,
            dev,
            directory,
            depth
        )
    }

    treeview = build_file_tree(tree)
    rprint(treeview)


def run_download(
    tps: GeoCom,
    filename: str,
    file: BufferedWriter,
    device: str = "internal",
    filetype: str = "unknown",
    chunk: int = 450,
    large: bool = False
) -> None:
    setup = tps.ftr.setup_download
    download = tps.ftr.download
    if large:
        setup = tps.ftr.setup_large_download
        download = tps.ftr.download_large

    resp_setup = setup(
        filename,
        chunk,
        _DEVICE[device],
        _FILE[filetype]
    )
    if resp_setup.error != GeoComCode.OK or resp_setup.params is None:
        echo_red(f"Could not set up file download ({resp_setup.error.name})")
        return

    block_count = resp_setup.params
    with progressbar(
        range(block_count),
        label="Downloading"
    ) as bar:
        for i in bar:
            resp_pull = download(i + 1)
            if resp_pull.error != GeoComCode.OK or resp_pull.params is None:
                echo_red(
                    "An error occured during download "
                    f"({resp_setup.error.name})"
                )
                return

            echo(bytes.fromhex(resp_pull.params), file, False)

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
    chunk: int = 450,
    large: bool = False
) -> None:
    with open_serial(
        port=port,
        speed=baud,
        timeout=timeout,
        retry=retry,
        sync_after_timeout=sync_after_timeout
    ) as com:
        tps = GeoCom(com)
        try:
            run_download(tps, filename, output, device, filetype, chunk, large)
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
    filetype: str = "unknown",
    recursive: bool = False,
    depth: str = "1"
) -> None:
    with open_serial(
        port=port,
        speed=baud,
        timeout=timeout,
        retry=retry,
        sync_after_timeout=sync_after_timeout
    ) as com:
        tps = GeoCom(com)
        try:
            if not recursive:
                run_listing(tps, device, directory, filetype)
            else:
                run_listing_tree(tps, device, directory, int(depth))
        finally:
            tps.ftr.abort_list()
