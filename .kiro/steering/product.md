# Product Overview

Trademan is an asynchronous Python trading helper for Tinkoff Invest clients with a Django backend. This is an educational pet project designed to improve MOEX (Moscow Stock Exchange) functionality and automate trading tasks.

## Core Purpose

- Buy/sell stocks and futures at better prices without manual intervention
- Create market-neutral positions using calendar spreads (future as far leg, future/stock as near leg)
- Automate routine tasks like placing stop orders and canceling orders at maximum speed
- Provide market scanning capabilities for profitable trading opportunities

## Architecture

The system consists of two main components:

- **Bot** (Frontend): Telegram bot interface that takes commands, executes them, and reports status/errors
- **Base** (Backend): Django REST API that manages database, configurations, and provides web interface

## Key Features

- Asynchronous order processing with real-time monitoring
- Calendar spread trading with automatic position balancing
- Bulk stop order placement with customizable levels
- Market scanning for profitable stock-future pairs
- Dividend scanning for futures
- Portfolio dumping and position management

## Important Notes

- This is NOT a trading robot but a helper tool for better execution
- Educational product - use at your own risk with real assets
- Russian language interface (Tinkoff Broker requirement)
- Designed for Raspberry Pi deployment via Docker