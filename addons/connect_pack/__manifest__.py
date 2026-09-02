{
    "name": "Connect Pack ERP",
    "version": "19.0.1.0.0",
    "summary": "Company-tailored ERP customisations for Connect Pack",
    "description": """
Connect Pack ERP
================
Umbrella module that tailors Odoo Community to Connect Pack's processes:
purchasing, inventory, sales, manufacturing / work orders, estimations
(مقايسات), production follow-up and HR.

It depends on the standard apps the company relies on and ships the first
custom workflow: the Estimation (مقايسة) document. Split into focused
sub-modules (connect_pack_sale, connect_pack_mrp, ...) as the scope grows.
""",
    "author": "Connect Pack",
    "website": "https://github.com/KarimSaadElbaz/Connect-Pack-ERP",
    "category": "Connect Pack",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "contacts",
        "sale_management",
        "purchase",
        "stock",
        "mrp",
        "account",
        "hr",
        "project",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "views/estimation_views.xml",
        "views/connect_pack_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "connect_pack/static/src/language_switch/language_switch.js",
            "connect_pack/static/src/language_switch/language_switch.xml",
        ],
    },
    "application": True,
    "installable": True,
}
