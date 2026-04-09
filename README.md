# Store Management System

A microservice-based e-commerce platform built with **Flask**, **MySQL**, **Docker**, and **Ethereum blockchain** (Solidity smart contracts via Ganache). The system supports user authentication with JWT tokens, product management, order processing, delivery tracking, and blockchain-powered payment/delivery contracts.

---

## Architecture Overview

The system is composed of multiple Docker containers orchestrated via Docker Compose:

| Service          | Port  | Description                                      |
|------------------|-------|--------------------------------------------------|
| **auth-app**     | 5000  | Authentication service (registration, login, JWT)|
| **owner-app**    | 5001  | Store owner service (product/category management)|
| **customer-app** | 5002  | Customer service (search, order, delivery)       |
| **courier-app**  | 5003  | Courier service (pickup and deliver orders)      |
| **auth-db**      | 3306  | MySQL database for user data                     |
| **shop-db**      | 3307  | MySQL database for shop data                     |
| **ganache**      | 8545  | Ethereum blockchain simulator                    |
| **adminer**      | 8080  | Database administration UI                       |

---

## Tech Stack

- **Backend:** Python 3, Flask, Flask-SQLAlchemy, Flask-Migrate, Flask-JWT-Extended
- **Databases:** MySQL (via PyMySQL)
- **Blockchain:** Solidity 0.8.18, Web3.py, Ganache CLI
- **Containerization:** Docker, Docker Compose
- **Smart Contract Compilation:** Solc (via Docker)

---

## Getting Started

### 1. Start all services (development mode)

```bash
docker compose -f development.yaml up
```

This starts all containers with hot-reload volume mounts for source code.

### 2. Start all services (production mode)

```bash
docker compose -f deployment.yaml up
```

### 3. Stop and clean up

```bash
docker compose -f development.yaml down --volumes --remove-orphans
```

---

## API Endpoints

### Authentication Service (port 5000)

| Method | Endpoint              | Description                     | Auth |
|--------|-----------------------|---------------------------------|------|
| POST   | `/register_customer`  | Register a new customer         | No   |
| POST   | `/register_courier`   | Register a new courier          | No   |
| POST   | `/login`              | Login and get JWT token         | No   |
| POST   | `/delete`             | Delete user                     | JWT  |

### Owner Service (port 5001)

| Method | Endpoint               | Description                                      | Auth  |
|--------|------------------------|--------------------------------------------------|-------|
| POST   | `/update`              | Upload CSV to add products and categories        | Owner |
| GET    | `/product_statistics`  | Get sold/waiting quantities per product          | Owner |
| GET    | `/category_statistics` | Get categories sorted by completed order volume  | Owner |

### Customer Service (port 5002)

| Method | Endpoint              | Description                                      | Auth     |
|--------|-----------------------|--------------------------------------------------|----------|
| GET    | `/search`             | Search products by name and/or category          | Customer |
| POST   | `/order`              | Place a new order                                | Customer |
| GET    | `/status`             | View all orders for the authenticated customer   | Customer |
| POST   | `/delivered`          | Confirm delivery of an order                     | Customer |
| POST   | `/generate_invoice`   | Generate blockchain invoice for payment          | Customer |

### Courier Service (port 5003)

| Method | Endpoint              | Description                          | Auth    |
|--------|-----------------------|--------------------------------------|---------|
| GET    | `/orders_to_deliver`  | List all orders with CREATED status  | Courier |
| POST   | `/pick_up_order`      | Pick up an order for delivery        | Courier |

---

## Blockchain / Smart Contract

The `DeliveryContract.sol` implements a delivery workflow with the following stages:

1. **CREATED** — Contract deployed when a customer places an order.
2. **PAID** — Customer pays the total price via the `invoice()` function.
3. **PICKUP** — Courier is assigned via `pick_up_order()`.
4. **COMPLETE** — Customer confirms delivery via `delivered()`. Funds are distributed: 80% to the owner, 20% to the courier.

### Compile the Solidity Contract

```powershell
powershell.exe -ExecutionPolicy Bypass -File .\compile.ps1 -file_path "DeliveryContract.sol"
```

### Generate Ethereum Keystore

```bash
python keystore_generator.py
```

This creates `owner_keys.json` used by the shop services to sign blockchain transactions.

---

## Database Migrations

### Inside Docker containers

```bash
# Auth service
./auth_migrate.sh

# Shop service
./shop_migrate.sh
```

### Reset databases

```bash
# Reset auth database
docker exec -i <auth-db-container> mysql -u root -proot users < restart_auth.sql

# Reset shop database
docker exec -i <shop-db-container> mysql -u root -proot shops < restart_shop.sql
```

---

## Database Schema

### Auth Database (`users`)

- **User** — `id`, `email`, `password`, `forename`, `surname`, `role_id`
- **Role** — `id`, `name` (customer / courier / owner)

A default owner account is seeded on startup: `onlymoney@gmail.com`.

### Shop Database (`shops`)

- **Product** — `id`, `name`, `price`
- **Category** — `id`, `name`
- **ProductCategory** — many-to-many relationship
- **Order** — `id`, `price`, `status`, `time_created`, `customer_email`, `public_bc_address`
- **OrderItem** — `order_id`, `product_id`, `quantity`

Order statuses: `CREATED` → `PENDING` → `COMPLETE`.

---

## Running Tests

### Install test dependencies

```bash
pip install -r Tests/requirements.txt
```

### Run authentication tests

```bash
python Tests/main.py --type authentication \
    --authentication-url http://127.0.0.1:5000 \
    --jwt-secret JWT_SECRET_DEV_KEY \
    --roles-field roles \
    --owner-role owner \
    --customer-role customer \
    --courier-role courier
```

### Run shop tests (all levels, with authentication and blockchain)

```bash
python Tests/main.py --type level3 \
    --with-authentication \
    --authentication-url http://127.0.0.1:5000 \
    --owner-url http://127.0.0.1:5001 \
    --customer-url http://127.0.0.1:5002 \
    --courier-url http://127.0.0.1:5003 \
    --with-blockchain \
    --provider-url http://127.0.0.1:8545 \
    --owner-private-key 0xb64be88dd6b89facf295f4fd0dda082efcbe95a2bb4478f5ee582b7efe88cf60
```

### Test levels

| Level  | Scope                                              |
|--------|----------------------------------------------------|
| level0 | Product update (CSV upload) and search              |
| level1 | Order creation and order status                     |
| level2 | Courier pickup and customer delivery confirmation   |
| level3 | Product and category statistics                     |

Higher levels include all lower-level tests.

---

## Local Development (without Docker)

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r Shop/requirements.txt
pip install -r Authentication/requirements.txt
```

Ensure MySQL is running locally on port 3306 and Ganache on port 8545.

---

## Adminer (Database UI)

Access at [http://localhost:8080](http://localhost:8080) when containers are running.

- **Auth DB:** Server: `auth-db`, User: `root`, Password: `root`, Database: `users`
- **Shop DB:** Server: `shop-db`, User: `root`, Password: `root`, Database: `shops`
