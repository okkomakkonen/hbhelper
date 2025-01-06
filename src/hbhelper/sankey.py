from decimal import Decimal

from .homebank import Category, read_homebank


def create_sankey(filename: str, year: int) -> str:
    """Create a Sankey diagram for the financial data for the given year"""

    out = ""

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

    out += "Input the following on https://sankeymatic.com/build/\n"

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
                if child.amount > 0:
                    out += f"{child.full_name} [{child.amount}] {parent.full_name}\n"

                elif child.amount < 0:
                    out += f"{parent.full_name} [{-child.amount}] {child.full_name}\n"

    out += "Revenue [*] Profit"

    return out
