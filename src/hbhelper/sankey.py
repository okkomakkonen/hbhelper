from decimal import Decimal
import datetime

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


def create_sankey(
    filename: str,
    begin: datetime.date,
    end: datetime.date,
    ignore: tuple[str] | None = None,
) -> str:
    """Create a Sankey diagram for the financial data for the given year"""

    sankeymatic_filename = "hbhelper_sankey_source.txt"

    f = open(sankeymatic_filename, "+w")
    f.write(PREAMBLE)

    # read the Homebank file into the internal format
    accounts, categories, operations = read_homebank(filename)

    # track the amount of transactions that are not categorized
    other = Decimal(0)

    # collect the amounts from the transactions within the date range to their categories
    for operation in operations:
        if not (begin <= operation.date < end):
            continue

        if operation.category is None:
            other += operation.amount
        else:
            operation.category.amount += operation.amount

    # add the "Other" (sub)categories for top level categories
    for parent in categories:
        if parent.amount != 0 and parent.children:
            parent.children.append(
                Category(name="Other", parent=parent, amount=parent.amount)
            )
            parent.amount = Decimal(0)

    categories.append(Category(name="Other", amount=other))

    # sort categories by their amount with biggest first
    categories = sorted(
        categories, key=lambda category: abs(category.total), reverse=True
    )

    # loop through the parent categories
    for parent in categories:
        # ignore unnecessary categories
        if ignore and parent.name in ignore:
            continue

        # put the categories with positive totals on the left
        if parent.total > 0:
            f.write(f"{parent.full_name} [{parent.total}] Budget\n")

        # put the categories with negative totals on the right
        if parent.total < 0:
            f.write(f"Budget [{-parent.total}] {parent.full_name}\n")

            # separate the subcategories
            if parent.children is None:
                continue

            children = sorted(parent.children, key=lambda category: category.total)

            for child in children:
                if ignore and child.full_name in ignore:
                    continue

                if child.amount > 0:
                    f.write(f"{child.full_name} [{child.amount}] {parent.full_name}\n")

                elif child.amount < 0:
                    f.write(f"{parent.full_name} [{-child.amount}] {child.full_name}\n")

    total = Decimal(sum(parent.total for parent in categories))

    # extra revenue is profit
    # TODO: fix this
    if total > 0:
        f.write(f"Budget [{total}] Profit\n")
    elif total < 0:
        f.write(f"Loss [{-total}] Budget")
    f.write(SETTINGS)
    f.close()

    return f"Wrote SankeyMATIC diagram inputs to {sankeymatic_filename}, visit https://sankeymatic.com/build/ to create diagram"
