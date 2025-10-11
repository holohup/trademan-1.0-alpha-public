# Project Structure

## Root Level Organization

```
trademan-1.0-alpha-public/
├── bot/                    # Telegram bot service (frontend)
├── trademan/              # Django REST API service (backend)
├── tests/                 # Test suites for both services
├── docker-compose.yml     # Container orchestration
├── requirements-tests.txt # Testing dependencies
├── pytest.ini           # Test configuration
└── setup.cfg            # Code quality configuration
```

## Bot Service Structure (`/bot`)

```
bot/
├── main.py              # Bot entry point
├── bot_init.py          # Bot initialization
├── settings.py          # Bot configuration
├── commands.py          # Telegram command handlers
├── instant_commands.py  # Quick response commands
├── requirements.txt     # Bot dependencies
├── .env                # Environment variables
├── scanner/            # Market scanning functionality
├── tools/              # Utility modules
│   ├── adapters.py     # Data adapters
│   ├── cache.py        # Caching utilities
│   ├── classes.py      # Core data classes
│   ├── orders.py       # Order management
│   ├── trading_hours.py # Market hours logic
│   ├── trading_time.py # Time utilities
│   └── utils.py        # General utilities
├── cancel_all_orders.py # Order cancellation
├── place_stops.py      # Stop order placement
├── queue_handler.py    # Async queue processing
├── sellbuy.py         # Buy/sell operations
├── spreads.py         # Spread trading logic
└── stop_orders.py     # Stop order management
```

## Base Service Structure (`/trademan`)

```
trademan/
├── manage.py           # Django management script
├── requirements.txt    # Django dependencies
├── db.sqlite3         # SQLite database
├── .env               # Environment variables
├── trademan/          # Django project settings
│   ├── settings.py    # Main configuration
│   ├── urls.py        # URL routing
│   ├── wsgi.py        # WSGI application
│   └── daily_updater.py # Middleware for data updates
├── base/              # Core Django app
│   ├── models.py      # Database models
│   ├── admin.py       # Admin interface
│   ├── apps.py        # App configuration
│   ├── migrations/    # Database migrations
│   └── management/    # Custom management commands
└── api/               # REST API app
    ├── urls.py        # API URL routing
    ├── apps.py        # API app configuration
    ├── migrations/    # API migrations
    └── v1/            # API version 1
```

## Test Structure (`/tests`)

```
tests/
├── bot_tests/                    # Bot service tests
│   ├── classes_tests/           # Core class tests
│   │   ├── adapters_test.py
│   │   ├── cache_test.py
│   │   ├── trading_time_test.py
│   │   ├── asset_tests/         # Asset-related tests
│   │   ├── data_process_tests/  # Data processing tests
│   │   └── spread_tests/        # Spread logic tests
│   ├── instant_commands_tests/  # Command tests
│   ├── spread_yield_tests/      # Yield calculation tests
│   ├── stops_tests/            # Stop order tests
│   └── utils_tests/            # Utility tests
└── trademan_tests/             # Django service tests
    ├── api_tests/              # API endpoint tests
    ├── test_models/            # Model tests
    ├── fixtures/               # Test data
    └── update_tests/           # Data update tests
```

## Key Conventions

### File Naming
- Snake_case for Python files and directories
- Descriptive names indicating functionality
- Test files end with `_test.py` or `_tests.py`

### Module Organization
- **Separation of Concerns**: Bot handles UI/commands, Base handles data/API
- **Tools Directory**: Shared utilities and helper functions
- **API Versioning**: REST API organized by version (`v1/`)
- **Test Mirroring**: Test structure mirrors source code organization

### Configuration Files
- **Environment Variables**: `.env` files in both services (not committed)
- **Sample Files**: `.env.sample` files provide templates
- **Settings Modules**: Centralized configuration in `settings.py` files
- **Docker Configuration**: `Dockerfile` in each service directory

### Database & Migrations
- **SQLite**: Single file database for simplicity
- **Django Migrations**: Standard Django migration system
- **Model Organization**: Core models in `base/models.py`

### Dependencies
- **Service-Specific**: Each service has its own `requirements.txt`
- **Test Dependencies**: Separate `requirements-tests.txt` at root
- **Version Pinning**: All dependencies pinned to specific versions

## Development Workflow

1. **Local Development**: Use virtual environments for each service
2. **Testing**: Run pytest from project root with proper PYTHONPATH
3. **Code Quality**: flake8 and mypy checks before commits
4. **Deployment**: Docker Compose for production/staging environments
5. **Database Updates**: Django management commands for data synchronization