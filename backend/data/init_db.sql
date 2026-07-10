"""
PostgreSQL Database Initialization Script
Run once to create the database and user.
"""

-- Create database and user
CREATE USER farmer_user WITH PASSWORD 'farmer_pass';
CREATE DATABASE farming_db OWNER farmer_user;
GRANT ALL PRIVILEGES ON DATABASE farming_db TO farmer_user;

-- Connect to farming_db and create schema
\c farming_db

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- for text search

-- All tables are auto-created by SQLAlchemy on startup via init_db()
-- To apply manually, run: python -c "import asyncio; from app.core.database import init_db; asyncio.run(init_db())"
