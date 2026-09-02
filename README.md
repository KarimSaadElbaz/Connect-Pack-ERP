# Connect Pack ERP

Company-tailored ERP for **Connect Pack**, built as custom modules on top of
**Odoo 19 Community** (free edition). Odoo core is **not** part of this repo — it
is pulled as a Docker image. This repo contains only our own addons.

## Scope (target)

| Area | Base app used | Status |
|------|---------------|--------|
| Sales / quotations | `sale_management` | standard |
| Purchasing | `purchase` | standard |
| Inventory / warehouses | `stock` | standard |
| Manufacturing / work orders | `mrp` | standard |
| Accounting / invoicing | `account` | standard (Community = invoicing; extend with OCA later) |
| HR | `hr` | standard |
| Estimations (مقايسات) | **custom** | ✅ first workflow shipped |
| Production follow-up | `project` / `mrp` | to design |

## Requirements

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose

## Quick start (local)

```bash
cp .env.example .env
docker compose up -d
```

Then open http://localhost:8069, create a database (master password is
`change-me-please`, see `config/odoo.conf`), and in **Apps** remove the
"Apps" filter, search **Connect Pack ERP**, and install it.

Stop with `docker compose down` (add `-v` to also wipe the database + filestore).

## Repo layout

```
addons/connect_pack/      the umbrella custom module
  __manifest__.py         dependencies + data files
  models/estimation.py    connect.pack.estimation + .line
  security/               access rules
  data/                   sequences
  views/                  form / list / search / menus
config/odoo.conf          Odoo config mounted into the container
docker-compose.yml        Odoo 19 + PostgreSQL 16
```

## Roadmap

1. Split `connect_pack` into focused sub-modules as features land
   (`connect_pack_sale`, `connect_pack_mrp`, ...).
2. Proper security groups (Estimation User / Manager) instead of
   `base.group_user` / `base.group_system`.
3. Convert a confirmed estimation into a Sale Order and/or MRP order.
4. Egyptian accounting: evaluate OCA `account-financial-reporting` and an
   ETA e-invoice integration.

## Deployment notes

Odoo needs persistent storage for its filestore and a real PostgreSQL, so the
free tier of app-only hosts (e.g. Render free web service) is not a good fit.
Cheapest reliable option: a small VPS (~€5/month) running this same
`docker-compose.yml` behind nginx + a Let's Encrypt certificate.

## License

The `connect_pack` module is licensed LGPL-3, matching Odoo Community.
