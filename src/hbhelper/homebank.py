import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal


def to_date(d: str) -> date:
    # 1970-1-1 is 719163 according to https://commoneraday.com/index.pl

    return date(1970, 1, 1) + timedelta(days=int(d) - 719163)


@dataclass
class Acc:
    key: str
    flags: str = ""
    pos: str = ""
    type: str = ""
    curr: str = ""
    name: str = ""
    number: str = ""
    bankname: str = ""
    initial: str = ""
    minimum: str = ""
    maximum: str = ""
    notes: str = ""
    rdate: str = ""


@dataclass
class Cat:
    key: str
    name: str = ""
    parent: str = ""  # category
    flags: str = ""


@dataclass
class Pay:
    key: str
    name: str = ""
    category: str = ""  # category


@dataclass
class Ope:
    date: str = ""
    amount: str = ""
    account: str = ""  # account
    dst_account: str = ""  # account
    st: str = ""
    flags: str = ""
    payee: str = ""  # payee
    category: str = ""  # category
    wording: str = ""
    tags: str = ""
    kxfer: str = ""
    scat: str = ""  # category
    samt: str = ""
    smem: str = ""


@dataclass
class Account:
    name: str = ""
    number: str = ""
    bankname: str = ""
    initial: Decimal = Decimal(0)
    notes: str = ""

    def __repr__(self):
        return self.name


@dataclass
class Category:
    name: str = ""
    parent: "Category | None" = None
    children: list["Category"] | None = None
    amount: Decimal = Decimal(0)

    @property
    def full_name(self) -> str:
        if self.parent:
            return f"{self.parent.name}:{self.name}"

        return self.name

    @property
    def total_of_children(self) -> Decimal:
        if self.children is None:
            return Decimal(0)
        return Decimal(sum(child.amount for child in self.children))

    @property
    def total(self) -> Decimal:
        return self.amount + self.total_of_children


@dataclass
class Operation:
    date: date
    amount: Decimal
    account: Account
    dst_account: Account | None = None
    payee: str = ""
    category: Category | None = None
    wording: str = ""


def read_homebank(
    filename: str,
) -> tuple[list[Account], list[Category], list[Operation]]:
    tree = ET.parse(filename)

    root = tree.getroot()

    accs: dict[str, Acc] = {}
    cats: dict[str, Cat] = {}
    pays: dict[str, Pay] = {}
    opes: list[Ope] = []

    for node in root:
        match node.tag:
            case "account":
                accs[node.attrib["key"]] = Acc(**node.attrib)

            case "cat":
                cats[node.attrib["key"]] = Cat(**node.attrib)

            case "pay":
                pays[node.attrib["key"]] = Pay(**node.attrib)

            case "ope":
                opes.append(Ope(**node.attrib))

    accounts: dict[str, Account] = {}
    categories_with_parent: dict[str, tuple[Category, str]] = {}
    categories: dict[str, Category] = {}
    operations: list[Operation] = []

    for key, acc in accs.items():
        account = Account(
            name=acc.name,
            number=acc.number,
            bankname=acc.bankname,
            initial=round(Decimal(acc.initial), 2),
            notes=acc.notes,
        )
        accounts[key] = account

    for key, cat in cats.items():
        category = Category(name=cat.name)
        categories_with_parent[key] = (category, cat.parent)

    for key, (category, parent_key) in categories_with_parent.items():
        categories[key] = category

        if not parent_key:
            continue

        if parent_key not in categories_with_parent:
            raise Exception("no parent category found")

        parent, _ = categories_with_parent[parent_key]

        category.parent = parent

        if parent.children is None:
            parent.children = []

        parent.children.append(category)

    for ope in opes:
        if not ope.samt:
            operation = Operation(
                date=to_date(ope.date),
                amount=round(Decimal(ope.amount), 2),
                account=accounts[ope.account],
                dst_account=accounts.get(ope.dst_account, None),
                payee=pays[ope.payee].name if ope.payee in pays else "",
                category=categories.get(ope.category, None),
                wording=ope.wording,
            )
            operations.append(operation)
        else:
            for amt, cat, mem in zip(
                ope.samt.split("||"), ope.scat.split("||"), ope.smem.split("||")
            ):
                operation = Operation(
                    date=to_date(ope.date),
                    amount=round(Decimal(amt), 2),
                    account=accounts[ope.account],
                    dst_account=None,
                    payee=pays[ope.payee].name if ope.payee in pays else "",
                    category=categories.get(cat, None),
                    wording=mem,
                )
                operations.append(operation)

    parent_categories = [
        category for category in categories.values() if category.parent is None
    ]

    return list(accounts.values()), parent_categories, operations
