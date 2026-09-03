"""Post-install setup for Connect Pack.

Seeds the three physical warehouses the company operates and the storage
zones inside each one. Everything here is idempotent so it is safe to run
again on module update or on a fresh server install.
"""

# code -> (name, [storage zones inside the warehouse's stock location])
WAREHOUSES = [
    (
        "RAW",
        "مخزن الخامات ومستلزمات الإنتاج",
        [
            "أحبار",
            "غراء ولواصق",
            "دبابيس وسلك",
            "أشرطة ولفّ",
            "كيماويات",
            "قطع غيار ماكينات",
            "مستهلكات عامة",
        ],
    ),
    (
        "PAP",
        "مخزن الورق والكرتون",
        [
            "ورق أبيض",
            "ورق كرافت",
            "ورق مطبوع",
            "لفّات كرتون",
            "ألواح كرتون مضلّع",
            "كليشيهات وأسطمبات",
        ],
    ),
    (
        "FIN",
        "مخزن البضاعة المنتهية",
        [
            "تحت الفحص",
            "جاهز للتسليم",
            "مرتجعات",
            "تالف",
        ],
    ),
]

_OUR_CODES = {code for code, _name, _zones in WAREHOUSES}


def setup_warehouses(env):
    company = env.company or env["res.company"].search([], order="id", limit=1)
    Warehouse = env["stock.warehouse"].with_company(company)
    Location = env["stock.location"].with_company(company)

    # Odoo auto-creates one default warehouse when `stock` is installed.
    # Repurpose it as the first (raw materials) warehouse instead of leaving
    # an unused extra one around.
    default_wh = Warehouse.search(
        [("company_id", "=", company.id), ("code", "not in", list(_OUR_CODES))],
        order="id",
        limit=1,
    )

    for code, name, zones in WAREHOUSES:
        warehouse = Warehouse.search(
            [("code", "=", code), ("company_id", "=", company.id)], limit=1
        )
        if not warehouse and default_wh:
            warehouse = default_wh
            default_wh = Warehouse.browse()  # only reuse it once
            warehouse.write({"name": name, "code": code})
        elif not warehouse:
            warehouse = Warehouse.create(
                {"name": name, "code": code, "company_id": company.id}
            )
        else:
            warehouse.name = name

        parent = warehouse.lot_stock_id
        for zone in zones:
            already = Location.search(
                [("name", "=", zone), ("location_id", "=", parent.id)], limit=1
            )
            if not already:
                Location.create(
                    {
                        "name": zone,
                        "location_id": parent.id,
                        "usage": "internal",
                        "company_id": company.id,
                    }
                )


def post_init_hook(env):
    setup_warehouses(env)
