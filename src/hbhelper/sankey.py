from decimal import Decimal

from .homebank import Category, read_homebank

PREAMBLE = """// SankeyMATIC diagram inputs - Created by hbhelper
// https://sankeymatic.com/build/

// === Nodes and Flows ===

"""

SETTINGS = """
// === Settings ===

size w 1200
  h 900
margin l 12
  r 12
  t 18
  b 20
bg color #ffffff
  transparent N
node w 13
  h 57.5
  spacing 100
  border 0
  theme c
  color #888888
  opacity 1
flow curvature 0.62
  inheritfrom outside-in
  color #999999
  opacity 0.4
layout order exact
  justifyorigins N
  justifyends N
  reversegraph N
  attachincompletesto nearest
labels color #000000
  hide N
  highlight 0
  fontface sans-serif
  linespacing 0.2
  relativesize 114
  magnify 110
labelname appears Y
  size 10.5
  weight 400
labelvalue appears Y
  fullprecision Y
  position after
  weight 400
labelposition autoalign 0
  scheme auto
  first before
  breakpoint 5
value format ',.'
  prefix ''
  suffix ''
themeoffset a 6
  b 0
  c 0
  d 0
meta mentionsankeymatic Y
  listimbalances Y
"""


def create_sankey(filename: str, year: int, ignore: tuple[str] | None = None) -> str:
    """Create a Sankey diagram for the financial data for the given year"""

    out = PREAMBLE

    accounts, categories, operations = read_homebank(filename)

    other = Decimal(0)

    for operation in operations:
        if operation.date.year != year:
            continue

        if operation.category is None:
            other += operation.amount
        else:
            operation.category.amount += operation.amount

    assert other == 0

    for category in categories:
        if category.amount != 0 and category.children:
            category.children.append(
                Category(name="Other", parent=category, amount=category.amount)
            )
            category.amount = Decimal(0)

    categories = sorted(
        categories, key=lambda category: abs(category.total), reverse=True
    )

    for parent in categories:
        if ignore and parent.name in ignore:
            continue

        if parent.total > 0:
            out += f"{parent.full_name} [{parent.total}] Revenue\n"

        if parent.total < 0:
            out += f"Revenue [{-parent.total}] {parent.full_name}\n"

            if parent.children is None:
                continue

            children = list(
                sorted(parent.children, key=lambda category: category.total)
            )

            if parent.amount != 0:
                out += f"{parent.full_name} [{-parent.amount}] {parent.name}:Other\n"

            for child in children:
                if ignore and child.full_name in ignore:
                    continue

                if child.amount > 0:
                    out += f"{child.full_name} [{child.amount}] {parent.full_name}\n"

                elif child.amount < 0:
                    out += f"{parent.full_name} [{-child.amount}] {child.full_name}\n"

    out += "Revenue [*] Profit\n"

    out += SETTINGS

    filename = "hbhelper_sankey_source.txt"

    with open(filename, "+w") as f:
        f.write(out)

    return f"Wrote SankeyMATIC diagram inputs to {filename}, visit https://sankeymatic.com/build/ to create diagram"
