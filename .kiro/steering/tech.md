# Technology Stack

## Core Technologies

- **Python 3.9** (specifically for Raspberry Pi OS compatibility)
- **Django 2.2.19** with Django REST Framework 3.12.4
- **SQLite** database
- **Docker & Docker Compose** for containerized deployment
- **Asyncio** for asynchronous operations
- **AIogram 2.22.1** for Telegram bot functionality
- **Tinkoff Investments SDK 0.2.0b54** for broker API integration

## Key Dependencies

### Bot Service
- `tinkoff-investments==0.2.0b54`
- `aiogram==2.22.1` 
- `aiohttp==3.8.2`
- `python-dotenv==0.21.0`
- `protobuf==3.20.2`

### Base Service (Django)
- `django==2.2.19`
- `djangorestframework==3.12.4`
- `tinkoff-investments==0.2.0b54`
- `python-dotenv==0.21.0`

### Testing & Code Quality
- `pytest-django==4.5.2`
- `pytest-asyncio==0.20.3`
- `pytest-mock==3.10.0`
- `factory-boy==3.2.1`
- `flake8==5.0.4` with various plugins
- `mypy` for type checking

## Build & Development Commands

### Local Development Setup
```bash
# Bot service
cd bot && python3.9 -m venv venv && source venv/bin/activate && pip install -r requirements.txt

# Base service  
cd trademan && python3.9 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python manage.py migrate
```

### Running Services
```bash
# Base service (Django)
cd trademan && source venv/bin/activate && python manage.py runserver

# Bot service
cd bot && source venv/bin/activate && python main.py
```

### Docker Deployment
```bash
# Full stack deployment
docker-compose up -d

# Database setup (first time)
chmod 757 trademan && docker-compose exec web python manage.py migrate

# Restart after setup
docker-compose down && docker-compose up -d
```

### Testing
```bash
# Run tests (from project root)
pytest

# Code quality checks
flake8
mypy
```

### Django Management Commands
```bash
# Create superuser
python manage.py createsuperuser

# Update FIGI data from Tinkoff API
python manage.py update

# Health check
python manage.py check
```

## Configuration Notes

- **Python 3.9 Required**: Specific version for Raspberry Pi compatibility and asyncio loop handling
- **Decimal Handling**: Django REST Framework configured with `'COERCE_DECIMAL_TO_STRING': True`
- **Time Zone**: Europe/Moscow for MOEX trading hours
- **Language**: Russian (ru) for Tinkoff Broker integration
- **Environment Variables**: Both services use `.env` files for sensitive configuration