# type: ignore

from typing import List, Tuple

from svgwrite import Drawing
from svgwrite.container import Group
from svgwrite.shapes import Circle

from src.constants import DEFAULT_COLOR
from src.publisher.render.style import style, style_no_animation


def format_number(num: int) -> str:
    if num > 10000:
        return "~" + str(int(num / 1000)) + "k lines"
    elif num > 1000:
        return "~" + str(int(num / 100) / 10) + "k lines"
    elif num > 100:
        return "~" + str(int(num / 100) * 100) + " lines"
    else:
        return "<100 lines"


def get_template(
    width: int,
    height: int,
    padding: int,
    header_text: str,
    subheader_text: str,
    use_animation: bool = True,
    debug: bool = False,
) -> Tuple[Drawing, Group]:
    d = Drawing(size=(width, height))
    d.defs.add(d.style(style if use_animation else style_no_animation))

    d.add(
        d.rect(
            size=(width - 1, height - 1),
            insert=(0.5, 0.5),
            rx=4.5,
            stroke="#e4e2e2",
            fill="#fffefe",
        )
    )

    d.add(
        d.rect(
            size=(width - 2 * padding, height - 2 * padding),
            insert=(padding, padding),
            fill="#eee" if debug else "#fff",
        )
    )

    dp = Group(transform="translate(" + str(padding) + ", " + str(padding) + ")")

    dp.add(d.text(header_text, insert=(0, 13), class_="header"))
    dp.add(d.text(subheader_text, insert=(0, 31), class_="subheader"))

    return d, dp


def get_bar_section(
    d: Drawing,
    dataset: List[Tuple[str, str, List[Tuple[float, str]]]],
    padding: int = 45,
    bar_width: int = 210,
) -> Group:
    section = Group(transform="translate(0, " + str(padding) + ")")
    for i, (top_text, right_text, data_row) in enumerate(dataset):
        translate = "translate(0, " + str(40 * i) + ")"
        row = Group(transform=translate)
        row.add(d.text(top_text, insert=(2, 15), class_="lang-name"))
        row.add(d.text(right_text, insert=(bar_width + 10, 33), class_="lang-name"))
        progress = Drawing(width=str(bar_width), x="0", y="25")
        progress.add(
            d.rect(size=(bar_width, 8), insert=(0, 0), rx=5, ry=5, fill="#ddd")
        )
        total_percent, total_items = 0, len(data_row)
        for j, (percent, color) in enumerate(data_row):
            color = color or DEFAULT_COLOR
            percent = max(300 / bar_width, percent)
            bar_percent = bar_width * percent / 100
            bar_total = bar_width * total_percent / 100
            box_size, insert = (bar_percent, 8), (bar_total, 0)
            progress.add(d.rect(size=box_size, insert=insert, rx=5, ry=5, fill=color))

            width = min(bar_percent / 2, 5)
            if total_items > 1:
                box_left, box_right = j > 0, j < total_items - 1
                box_size, insert = bar_percent - 2 * width, bar_total + width
                if box_left:
                    box_size += width
                    insert -= width
                if box_right:
                    box_size += width
                progress.add(d.rect(size=(box_size, 8), insert=(insert, 0), fill=color))

            total_percent += percent
        row.add(progress)
        section.add(row)
    return section


def get_lang_name_section(
    d: Drawing, data: List[Tuple[str, str]], columns: int = 2, padding: int = 80
) -> Group:
    section = Group(transform="translate(0, " + str(padding) + ")")
    for i, x in enumerate(data):
        x_translate = str((260 / columns) * (i % columns))
        y_translate = str(20 * (i // columns))
        lang = Group(transform="translate(" + x_translate + ", " + y_translate + ")")
        lang.add(Circle(center=(5, 5), r=5, fill=(data[i][1] or DEFAULT_COLOR)))
        lang.add(d.text(data[i][0], insert=(14, 9), class_="lang-name"))
        section.add(lang)
    return section