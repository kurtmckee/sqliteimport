import dataclasses
import json
import pathlib
import platform
import typing

import click
import matplotlib.pyplot as plt

from . import STATS
from . import CodeType
from . import Importer
from . import Measurement


@click.command()
@click.option(
    "--code-type",
    type=CodeType,
    required=True,
    help=f"The code type to plot. Valid code types are: {', '.join(CodeType)}.",
)
@click.option(
    "--measurement",
    required=True,
    help=f"The measurement to plot. Valid values are: {', '.join(Measurement)}",
)
@click.option(
    "--output",
    type=pathlib.Path,
    help="If given, the plot will be saved to the given location.",
)
def plot(
    code_type: CodeType, measurement: Measurement, output: pathlib.Path | None
) -> None:
    """
    Plot the performance information.
    """

    if measurement == Measurement.time:
        config = get_time_stats(code_type)
    elif measurement == Measurement.size:
        config = get_size_stats(code_type)
    else:
        typing.assert_never(measurement)
    generate_plot(config)

    if output:
        plt.savefig(output)
    else:
        plt.show()


@dataclasses.dataclass
class Config:
    names: list[str]
    values: list[float]
    y_label: str
    title: str


def generate_plot(config: Config) -> None:
    bar_colors = ["tab:red", "tab:blue", "tab:orange"]

    fig, ax = plt.subplots()
    ax.bar(config.names, config.values, color=bar_colors)
    ax.set_ylabel(config.y_label)
    ax.set_title(config.title)


def get_time_stats(code_type: CodeType):
    stats_file = STATS / "stats.json"
    data = json.loads(stats_file.read_text())

    code_type_phrase = "source code" if code_type == CodeType.source else "bytecode"
    return Config(
        names=[str(importer) for importer in Importer],
        values=[
            data[Measurement.time][code_type][importer]["-cumulative_us"] / 1_000  # ms
            for importer in Importer
        ],
        y_label="Milliseconds",
        title=f"{platform.system()} {code_type_phrase} import times",
    )


def get_size_stats(code_type: CodeType):
    stats_file = STATS / "stats.json"
    data = json.loads(stats_file.read_text())

    code_type_phrase = "source code" if code_type == CodeType.source else "bytecode"
    return Config(
        names=[str(importer) for importer in Importer],
        values=[
            data["size"][importer][code_type] / 1_024 / 1_024 for importer in Importer
        ],
        y_label="Megabytes",
        title=f"{platform.system()} total {code_type_phrase} sizes",
    )
