# Implementation Plan

- [x] 1. Set up core infrastructure and state management

  - Create state management system for tracking spread creation sessions
  - Implement session storage with automatic cleanup
  - Add basic command handler structure for `/addspread`
  - _Requirements: 1.1, 1.2_

- [x] 1.1 Create spread state management module

  - Write tests for SpreadCreationState class and state management functions
  - Write `bot/spread_state.py` with SpreadCreationState class
  - Implement in-memory state storage with user_id as key
  - Add state persistence methods: save_state, get_state, clear_state, update_state
  - _Requirements: 1.1, 1.2_

- [x] 1.2 Create basic command handler for addspread

  - Write tests for command parsing and initial validation logic
  - Add `/addspread` command to ROUTINES in `bot/commands.py`
  - Create `bot/spread_creator.py` with handle_addspread_command function
  - Implement ticker parsing and validation from command arguments
  - _Requirements: 1.1, 1.4_

- [ ] 2. Implement ticker validation and API integration

  - Create API integration module for ticker validation
  - Add price fetching functionality using existing Tinkoff integration
  - Implement duplicate spread detection
  - _Requirements: 1.2, 1.3, 7.5_

- [ ] 2.1 Create API integration module for spread creation

  - Write tests for ticker validation and price fetching functions
  - Write `bot/spread_api.py` with ticker validation functions
  - Implement validate_ticker function using existing ticker endpoint
  - Add get_current_prices function using existing price fetching logic
  - _Requirements: 1.2, 1.3_

- [ ] 2.2 Add spread creation API endpoint integration

  - Write tests for spread creation and duplicate detection functions
  - Implement create_spread function to POST to Django spreads endpoint
  - Add check_duplicate_spread function to detect existing spreads
  - Handle API errors and connection issues gracefully
  - _Requirements: 6.1, 6.2, 7.4_

- [ ] 3. Implement market-neutral price calculation logic

  - Create price calculator module with ratio calculation
  - Implement spread price calculations for different asset type combinations
  - Add market-neutral explanation generation
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 3.1 Create spread pricing calculation module

  - Write tests for spread price calculations and ratio calculations for different asset combinations
  - Write `bot/spread_pricing.py` with calculate_spread_price function
  - Implement calculate_ratio function for stock-future and future-future pairs
  - Add get_market_neutral_explanation function for user display
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 3.2 Integrate price calculations with existing Tinkoff API

  - Write tests for price integration and error handling scenarios
  - Use existing get_current_prices_by_uid function for market data
  - Implement bid/ask price fetching for spread calculations
  - Add price unavailable handling and fallback logic
  - _Requirements: 2.5, 2.6_

- [ ] 4. Create interactive menu system with inline keyboards

  - Implement inline keyboard generators for each step
  - Create callback query handlers for menu interactions
  - Add menu navigation and state transitions
  - _Requirements: 2.4, 3.1, 4.1, 5.1_

- [ ] 4.1 Create inline keyboard menu generators

  - Write tests for menu generation functions and keyboard layouts
  - Write `bot/spread_menu.py` with menu generation functions
  - Implement generate_direction_menu for buy/sell selection
  - Add generate_price_menu and generate_amount_menu functions
  - Create generate_confirmation_menu for final review
  - _Requirements: 2.4, 3.1, 4.1, 5.1_

- [ ] 4.2 Implement callback query handlers

  - Write tests for callback handling and state transitions
  - Add callback query handler to `bot/spread_creator.py`
  - Implement state transitions based on user selections
  - Add input validation for custom price and amount entries
  - Handle menu navigation (back, cancel) functionality
  - _Requirements: 3.2, 3.4, 4.2, 4.4, 5.4_

- [ ] 5. Add comprehensive input validation and error handling

  - Implement validation for all user inputs (price, amount, tickers)
  - Add error message generation and user feedback
  - Create session timeout and cleanup mechanisms
  - _Requirements: 3.4, 4.4, 7.1, 7.3_

- [ ] 5.1 Implement input validation functions

  - Write tests for all validation functions with edge cases and error scenarios
  - Add price validation (valid integer, reasonable range)
  - Implement amount validation (positive integer, minimum lot requirements)
  - Create ticker format validation and existence checking
  - _Requirements: 3.2, 3.4, 4.2, 4.4_

- [ ] 5.2 Add comprehensive error handling and user feedback

  - Write tests for error handling scenarios and message generation
  - Implement error message generation for all validation failures
  - Add graceful handling of API connection errors
  - Create user-friendly error messages with suggested corrections
  - _Requirements: 7.1, 7.3, 7.4_

- [ ] 6. Integrate spread creation with Django backend

  - Connect menu system to Django API for spread persistence
  - Implement SpreadStats creation and association
  - Add success confirmation and spread activation
  - _Requirements: 5.5, 6.1, 6.2, 6.3_

- [ ] 6.1 Implement Django API integration for spread creation

  - Write tests for spread creation payload generation and API integration
  - Create spread creation payload from menu state
  - POST spread data to Django spreads endpoint
  - Handle SpreadStats creation automatically in Django
  - _Requirements: 5.5, 6.1, 6.2_

- [ ] 6.2 Add spread activation and confirmation

  - Write tests for spread activation and confirmation flow
  - Set active=True by default for new spreads
  - Return spread ID and confirmation to user
  - Clear session state after successful creation
  - _Requirements: 6.3, 6.4, 5.6_

- [ ] 7. Add logging, monitoring and session cleanup

  - Implement comprehensive logging for all operations
  - Add session timeout and automatic cleanup
  - Create monitoring for spread creation activity
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 7.1 Add comprehensive logging system

  - Write tests for logging functionality and log message formats
  - Log all spread creation attempts with user and parameters
  - Add error logging with full context for troubleshooting
  - Implement success logging with spread details
  - _Requirements: 7.1, 7.2, 7.3_

- [ ] 7.2 Create session cleanup and monitoring

  - Write tests for session timeout and cleanup functionality
  - Implement automatic session timeout (30 minutes)
  - Add periodic cleanup of stale sessions
  - Create monitoring dashboard for spread creation metrics
  - _Requirements: 7.1, 7.3_

- [ ] 8. Integration testing and final wiring

  - Connect all modules and test complete user flow
  - Add the addspread command to bot command routing
  - Verify integration with existing spreads trading functionality
  - _Requirements: 6.5_

- [ ] 8.1 Wire up complete spread creation flow

  - Write integration tests for complete user journey from command to spread creation
  - Register addspread command handler in bot dispatcher
  - Connect all modules: state management, API integration, menus, pricing
  - Test complete user journey from command to spread creation
  - _Requirements: 6.5_

- [ ] 8.2 Verify integration with existing spread trading system
  - Write integration tests for spread trading system compatibility
  - Ensure newly created spreads appear in spreads command
  - Test that created spreads are properly formatted for trading logic
  - Verify SpreadStats integration works with existing patch operations
  - _Requirements: 6.4, 6.5_
