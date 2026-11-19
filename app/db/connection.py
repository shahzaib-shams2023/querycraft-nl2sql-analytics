import sqlite3
from sqlalchemy import (
    create_engine, MetaData, Table, Column, Integer, String, Float, ForeignKey, DateTime, text
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timedelta
import os
from app.config import settings

Base = declarative_base()
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initializes schema and populates rich benchmark dataset if empty."""
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                plan_tier TEXT NOT NULL, -- Enterprise, Pro, Starter
                country TEXT NOT NULL,
                signup_date DATE NOT NULL
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                price REAL NOT NULL,
                cost REAL NOT NULL
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                order_date DATE NOT NULL,
                total_amount REAL NOT NULL,
                status TEXT NOT NULL, -- Completed, Processing, Cancelled
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(id),
                FOREIGN KEY (product_id) REFERENCES products(id)
            );
        """))
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                plan_name TEXT NOT NULL,
                monthly_mrr REAL NOT NULL,
                status TEXT NOT NULL, -- Active, Churned, Paused
                start_date DATE NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            );
        """))
        conn.commit()

        # Check if seed data exists
        res = conn.execute(text("SELECT COUNT(*) FROM customers")).scalar()
        if res == 0:
            _seed_data(conn)


def _seed_data(conn):
    """Seed realistic enterprise SaaS and eCommerce data."""
    customers = [
        ("Acme Corp", "ops@acmecorp.com", "Enterprise", "USA", "2024-01-15"),
        ("Globex Systems", "admin@globex.io", "Enterprise", "Germany", "2024-02-10"),
        ("Starlight Data", "tech@starlight.ai", "Pro", "UK", "2024-03-01"),
        ("Initech Software", "finance@initech.org", "Starter", "USA", "2024-04-12"),
        ("Umbrella Cloud", "devops@umbrellacloud.com", "Enterprise", "Japan", "2024-05-20"),
        ("Soylent Logistics", "procurement@soylent.co", "Pro", "Canada", "2024-06-18"),
        ("Cyberdyne Networks", "security@cyberdyne.io", "Enterprise", "USA", "2024-07-04"),
        ("Wayne Enterprises", "procurement@wayne.com", "Enterprise", "USA", "2024-08-11"),
        ("Hooli Labs", "gavin@hooli.xyz", "Starter", "USA", "2024-09-02"),
        ("Pied Piper AI", "richard@piedpiper.com", "Pro", "USA", "2024-10-14")
    ]
    for c in customers:
        conn.execute(
            text("INSERT INTO customers (name, email, plan_tier, country, signup_date) VALUES (:name, :email, :tier, :country, :date)"),
            {"name": c[0], "email": c[1], "tier": c[2], "country": c[3], "date": c[4]}
        )

    products = [
        ("Cloud Analytics Dedicated Node", "Infrastructure", 1200.0, 450.0),
        ("High-Throughput Vector Shard", "Database", 850.0, 310.0),
        ("Automated SIEM Log Ingestion Pack", "Security", 450.0, 120.0),
        ("Enterprise SSO & Audit Module", "Security", 300.0, 50.0),
        ("Realtime WebSocket Gateway", "Infrastructure", 600.0, 180.0),
        ("AI Code Review Agent License", "Developer Tools", 250.0, 40.0)
    ]
    for p in products:
        conn.execute(
            text("INSERT INTO products (name, category, price, cost) VALUES (:name, :cat, :price, :cost)"),
            {"name": p[0], "cat": p[1], "price": p[2], "cost": p[3]}
        )

    orders = [
        (1, "2024-10-01", 3600.0, "Completed"),
        (2, "2024-10-03", 2550.0, "Completed"),
        (3, "2024-10-07", 750.0, "Completed"),
        (4, "2024-10-10", 300.0, "Completed"),
        (5, "2024-10-15", 4800.0, "Completed"),
        (6, "2024-10-19", 1100.0, "Processing"),
        (7, "2024-10-22", 6400.0, "Completed"),
        (8, "2024-10-28", 12500.0, "Completed"),
        (9, "2024-11-01", 250.0, "Cancelled"),
        (10, "2024-11-05", 1450.0, "Completed"),
        (1, "2024-11-08", 2400.0, "Completed"),
        (2, "2024-11-12", 1700.0, "Completed")
    ]
    for o in orders:
        conn.execute(
            text("INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES (:cid, :odate, :amt, :status)"),
            {"cid": o[0], "odate": o[1], "amt": o[2], "status": o[3]}
        )

    order_items = [
        (1, 1, 3, 1200.0),
        (2, 2, 3, 850.0),
        (3, 4, 1, 300.0),
        (3, 3, 1, 450.0),
        (5, 1, 4, 1200.0),
        (7, 1, 4, 1200.0),
        (7, 3, 2, 450.0),
        (7, 4, 2, 350.0),
        (8, 1, 10, 1200.0),
        (8, 4, 1, 500.0),
        (10, 2, 1, 850.0),
        (10, 5, 1, 600.0)
    ]
    for oi in order_items:
        conn.execute(
            text("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (:oid, :pid, :qty, :uprice)"),
            {"oid": oi[0], "pid": oi[1], "qty": oi[2], "uprice": oi[3]}
        )

    subscriptions = [
        (1, "Enterprise Plus", 3500.0, "Active", "2024-01-15"),
        (2, "Enterprise Standard", 2200.0, "Active", "2024-02-10"),
        (3, "Pro Team", 750.0, "Active", "2024-03-01"),
        (4, "Starter Single", 150.0, "Paused", "2024-04-12"),
        (5, "Enterprise Dedicated", 4200.0, "Active", "2024-05-20"),
        (6, "Pro Team", 800.0, "Active", "2024-06-18"),
        (7, "Enterprise Plus", 5000.0, "Active", "2024-07-04"),
        (8, "Custom Corporate", 9500.0, "Active", "2024-08-11"),
        (9, "Starter Single", 120.0, "Churned", "2024-09-02"),
        (10, "Pro Team", 950.0, "Active", "2024-10-14")
    ]
    for s in subscriptions:
        conn.execute(
            text("INSERT INTO subscriptions (customer_id, plan_name, monthly_mrr, status, start_date) VALUES (:cid, :pname, :mrr, :status, :sdate)"),
            {"cid": s[0], "pname": s[1], "mrr": s[2], "status": s[3], "sdate": s[4]}
        )
    conn.commit()

