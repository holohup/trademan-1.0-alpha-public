# Design Document

## Overview

This design implements an interactive Telegram bot interface for creating spread pairs using aiogram 2.22.1's inline keyboard functionality. The system will provide a step-by-step guided process that validates tickers, displays market-neutral spread prices, and allows configuration through an intuitive menu system.

## Architecture

### Component Overview

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram Bot  │    │   Spread Creator │    │  Django API     │
│                 │    │                  │    │                 │
│ - Command Handler│◄──►│ - State Manager  │◄──►│ - Validation    │
│ - Inline Keyboard│    │ - Price Calculator│    │ - Persistence   │
│ - Callback Handler│   │ - Menu Generator │    │ - Ticker Lookup │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### State Management

The system will use a session-based state management approach to track the spread creation process:

```python
SpreadCreationState = {
    'user_id': int,
    'far_leg_ticker': str,
    'near_leg_ticker': str,
    'far_leg_data': dict,
    'near_leg_data': dict,
    'direction': str,  # 'buy' or 'sell'
    'custom_price': int,
    'amount': int,
    'current_step': str,  # 'ticker_validation', 'direction_selection', 'price_input', 'amount_input', 'confirmation'
}
```

## Components and Interfaces

### 1. Command Handler Module (`spread_creator.py`)

**Purpose:** Handle the initial `/addspread` command and coordinate the creation process.

**Key Functions:**
- `handle_addspread_command(message: types.Message)`: Parse tickers and initiate creation
- `validate_tickers(far_leg: str, near_leg: str)`: Validate ticker existence and API availability
- `create_initial_state(user_id: int, far_leg: str, near_leg: str)`: Initialize creation session

### 2. Interactive Menu Module (`spread_menu.py`)

**Purpose:** Generate and handle inline keyboard interactions.

**Key Functions:**
- `generate_direction_menu(state: dict)`: Create buy/sell selection menu
- `generate_price_menu(state: dict)`: Create price input interface
- `generate_amount_menu(state: dict)`: Create amount input interface
- `generate_confirmation_menu(state: dict)`: Create final confirmation screen

### 3. Price Calculator Module (`spread_pricing.py`)

**Purpose:** Calculate market-neutral spread prices and ratios.

**Key Functions:**
- `calculate_spread_price(far_leg_data: dict, near_leg_data: dict, direction: str)`: Calculate current market spread
- `calculate_ratio(far_leg_data: dict, near_leg_data: dict)`: Determine market-neutral ratio
- `get_market_neutral_explanation(far_leg: dict, near_leg: dict, direction: str)`: Generate explanation text

### 4. State Manager Module (`spread_state.py`)

**Purpose:** Manage creation session state and persistence.

**Key Functions:**
- `save_state(user_id: int, state: dict)`: Persist session state
- `get_state(user_id: int)`: Retrieve session state
- `clear_state(user_id: int)`: Clean up completed sessions
- `update_state(user_id: int, updates: dict)`: Update specific state fields

### 5. API Integration Module (`spread_api.py`)

**Purpose:** Interface with Django API for validation and creation.

**Key Functions:**
- `validate_ticker(ticker: str)`: Check ticker existence and trading availability
- `get_current_prices(figis: list)`: Fetch current market prices
- `create_spread(spread_data: dict)`: Create spread in database
- `check_duplicate_spread(far_leg: str, near_leg: str)`: Detect existing spreads

## Data Models

### Ticker Validation Response
```python
{
    'figi': str,
    'ticker': str,
    'name': str,
    'lot': int,
    'min_price_increment': Decimal,
    'asset_type': str,  # 'S', 'F', 'B'
    'api_trading_available': bool,
    'basic_asset_size': int,  # For futures
    'basic_asset': str,  # For futures
}
```

### Market Price Data
```python
{
    'figi': str,
    'bid_price': Decimal,
    'ask_price': Decimal,
    'last_price': Decimal,
}
```

### Spread Creation Data
```python
{
    'far_leg_figi': str,
    'near_leg_figi': str,
    'sell': bool,
    'price': int,
    'amount': int,
    'editable_ratio': int,  # Optional override
}
```

## Error Handling

### Validation Errors
- **Ticker Not Found**: "Ticker {ticker} not found in database"
- **API Trading Disabled**: "API trading not available for {ticker}"
- **Price Unavailable**: "Current prices unavailable for {ticker}"
- **Invalid Input**: "Please enter a valid {field_name}"

### System Errors
- **API Connection**: "Unable to connect to trading system. Please try again later."
- **Database Error**: "Error saving spread. Please contact administrator."
- **Session Timeout**: "Session expired. Please start over with /addspread"

### Error Recovery
- Graceful degradation when prices unavailable
- Session state persistence across bot restarts
- Automatic cleanup of stale sessions

## Testing Strategy

### Unit Tests
- **Price Calculation**: Test market-neutral calculations for different asset type combinations
- **Ratio Calculation**: Verify correct ratios for stock-future, future-future pairs
- **State Management**: Test state persistence and retrieval
- **Validation Logic**: Test ticker validation and error cases

### Integration Tests
- **API Integration**: Test Django API calls for validation and creation
- **Menu Flow**: Test complete user journey from command to confirmation
- **Error Handling**: Test error scenarios and recovery

### User Acceptance Tests
- **Happy Path**: Complete spread creation with valid inputs
- **Error Scenarios**: Invalid tickers, unavailable prices, duplicate spreads
- **Menu Navigation**: Back/cancel functionality, session management

## Implementation Flow

### Phase 1: Core Infrastructure
1. Set up state management system
2. Implement ticker validation API calls
3. Create basic command handler structure

### Phase 2: Price Calculation
1. Implement market-neutral price calculations
2. Add ratio calculation logic
3. Integrate with Tinkoff API for current prices

### Phase 3: Interactive Menus
1. Create inline keyboard generators
2. Implement callback query handlers
3. Add menu navigation logic

### Phase 4: Integration & Testing
1. Connect all components
2. Add comprehensive error handling
3. Implement session cleanup
4. Add logging and monitoring

## Security Considerations

- **User Authorization**: Verify user permissions using existing `is_me` filter
- **Input Validation**: Sanitize all user inputs before API calls
- **Session Security**: Implement session timeouts and cleanup
- **API Security**: Use existing token-based authentication for Django API

## Performance Considerations

- **State Storage**: Use in-memory storage with periodic cleanup for session state
- **API Caching**: Cache ticker validation results for short periods
- **Price Updates**: Implement price refresh mechanism for long-running sessions
- **Concurrent Sessions**: Support multiple users creating spreads simultaneously