# Requirements Document

## Introduction

This feature enables users to add new spread pairs directly through the Telegram bot interface using an interactive menu system, eliminating the need to access the Django admin panel. Users will initiate spread creation with a simple command containing two tickers, then use an interactive menu to configure the spread parameters.

## Requirements

### Requirement 1

**User Story:** As a trader, I want to initiate spread creation with a simple command, so that I can start the process without complex parameter syntax.

#### Acceptance Criteria

1. WHEN a user sends `/addspread <far_leg_ticker> <near_leg_ticker>` THEN the system SHALL validate both tickers exist
2. WHEN both tickers are valid THEN the system SHALL display an interactive configuration menu
3. WHEN a ticker doesn't exist THEN the system SHALL respond with "Ticker [ticker] not found"
4. WHEN the command format is incorrect THEN the system SHALL respond with usage instructions: "Usage: /addspread <far_leg_ticker> <near_leg_ticker>"
5. IF an asset doesn't support API trading THEN the system SHALL respond with "API trading not available for [ticker]"

### Requirement 2

**User Story:** As a trader, I want to see current market-neutral spread prices and configure spread direction through an interactive menu, so that I can make informed decisions about spread parameters.

#### Acceptance Criteria

1. WHEN the interactive menu is displayed THEN the system SHALL calculate and show current market-neutral spread price for buying the spread
2. WHEN the interactive menu is displayed THEN the system SHALL calculate and show current market-neutral spread price for selling the spread
3. WHEN calculating spread prices THEN the system SHALL use proper ratios (e.g., 1 future = 100 stocks for stock-future spreads, 1:1 for future-future spreads)
4. WHEN the interactive menu is displayed THEN the system SHALL provide buttons for "Buy Spread" and "Sell Spread" options
5. WHEN a direction is selected THEN the system SHALL update the display to show the selected direction and corresponding market-neutral calculation
6. WHEN prices are unavailable THEN the system SHALL display "Price unavailable" and disable related options

### Requirement 3

**User Story:** As a trader, I want to enter a custom spread price through the interactive menu, so that I can set my desired execution price for the market-neutral position.

#### Acceptance Criteria

1. WHEN a direction is selected THEN the system SHALL provide an input field for custom spread price
2. WHEN a custom price is entered THEN the system SHALL validate it's a valid integer
3. WHEN a custom price is entered THEN the system SHALL show the difference from current market-neutral spread price
4. WHEN the price input is invalid THEN the system SHALL display "Please enter a valid integer price"
5. WHEN no custom price is entered THEN the system SHALL use the current market-neutral spread price as default
6. WHEN displaying price difference THEN the system SHALL indicate if the custom price is better or worse than market

### Requirement 4

**User Story:** As a trader, I want to specify the amount to trade through the interactive menu, so that I can control the position size.

#### Acceptance Criteria

1. WHEN price is configured THEN the system SHALL provide an input field for trade amount
2. WHEN amount is entered THEN the system SHALL validate it's a positive integer
3. WHEN amount is entered THEN the system SHALL validate it meets minimum lot requirements
4. WHEN amount input is invalid THEN the system SHALL display "Please enter a valid positive amount"
5. WHEN amount is below minimum lot THEN the system SHALL display "Amount must be at least [lot_size] (minimum lot)"

### Requirement 5

**User Story:** As a trader, I want to review and confirm all spread parameters before creation, so that I can verify the market-neutral configuration is correct.

#### Acceptance Criteria

1. WHEN all parameters are configured THEN the system SHALL display a summary with far_leg, near_leg, direction, price, amount, calculated ratio, and market-neutral explanation
2. WHEN the summary is displayed THEN the system SHALL show what actions will be taken (e.g., "Sell 1 future, Buy 100 stocks" for selling a stock-future spread)
3. WHEN the summary is displayed THEN the system SHALL provide "Confirm" and "Cancel" buttons
4. WHEN "Confirm" is pressed THEN the system SHALL create the spread in the database
5. WHEN "Cancel" is pressed THEN the system SHALL abort the creation process
6. WHEN the spread is created THEN the system SHALL respond with "Spread created successfully with ID [id]"

### Requirement 6

**User Story:** As a trader, I want the new spread to be immediately available for trading, so that I don't need additional steps to activate it.

#### Acceptance Criteria

1. WHEN a spread is created THEN the system SHALL set active=True by default
2. WHEN a spread is created THEN the system SHALL create associated SpreadStats record
3. WHEN a spread is created THEN the system SHALL calculate ratio automatically based on asset types
4. WHEN a spread is created THEN the system SHALL make it available to the spreads trading command immediately
5. WHEN the spreads command is running THEN the system SHALL include newly created spreads in the next trading cycle

### Requirement 7

**User Story:** As a system administrator, I want proper error handling and logging, so that I can troubleshoot issues and monitor spread creation activity.

#### Acceptance Criteria

1. WHEN any error occurs during spread creation THEN the system SHALL log the error with full context
2. WHEN a spread is successfully created THEN the system SHALL log the creation with user and spread details
3. WHEN validation fails THEN the system SHALL log the validation failure with attempted parameters
4. WHEN database errors occur THEN the system SHALL handle them gracefully and respond with user-friendly messages
5. WHEN duplicate spreads are detected THEN the system SHALL respond with "Similar spread already exists with ID [id]"