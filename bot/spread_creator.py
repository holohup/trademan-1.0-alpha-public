"""
Spread creator module for handling /addspread command.

This module provides the main command handler for initiating spread creation
through the Telegram bot interface, including callback query handling for
interactive menus.
"""

from typing import Optional, Tuple
from aiogram import types
from spread_state import (
    SpreadCreationState,
    save_state,
    get_state,
    update_state,
    clear_state,
)
from spread_menu import (
    generate_direction_menu,
    generate_price_menu,
    generate_amount_menu,
    generate_confirmation_menu,
    format_direction_message,
    format_price_message,
    format_amount_message,
    format_spread_summary,
)
from spread_pricing import calculate_spread_price
from spread_api import create_spread
from bot_init import dp


def parse_addspread_command(args: str) -> Optional[Tuple[str, str]]:
    """
    Parse the addspread command arguments.

    Args:
        args: Command arguments string

    Returns:
        Tuple of (far_leg_ticker, near_leg_ticker) or None if invalid
    """
    if not args or not args.strip():
        return None

    # Split and clean up arguments
    tickers = args.strip().split()

    # Must have exactly 2 tickers
    if len(tickers) != 2:
        return None

    far_leg, near_leg = tickers[0].upper(), tickers[1].upper()
    return (far_leg, near_leg)


def validate_command_format(far_leg: Optional[str], near_leg: Optional[str]) -> bool:
    """
    Validate the command format and ticker values.

    Args:
        far_leg: Far leg ticker symbol
        near_leg: Near leg ticker symbol

    Returns:
        True if valid, False otherwise
    """
    # Check for None or empty values
    if not far_leg or not near_leg:
        return False

    # Check for empty strings after stripping
    if not far_leg.strip() or not near_leg.strip():
        return False

    # Check that tickers are different (case insensitive)
    if far_leg.upper() == near_leg.upper():
        return False

    return True


async def handle_addspread_command(message: types.Message) -> None:
    """
    Handle the /addspread command.

    Parses the command arguments, validates the format, and initiates
    the spread creation process by saving initial state.

    Args:
        message: Telegram message containing the command
    """
    user_id = message.from_user.id
    args = message.get_args()

    # Parse command arguments
    parsed_tickers = parse_addspread_command(args)

    if not parsed_tickers:
        await message.answer(
            "Usage: /addspread <far_leg_ticker> <near_leg_ticker>\n"
            "Example: /addspread GAZP GZZ4"
        )
        return

    far_leg_ticker, near_leg_ticker = parsed_tickers

    # Validate ticker format
    if not validate_command_format(far_leg_ticker, near_leg_ticker):
        await message.answer(
            "Usage: /addspread <far_leg_ticker> <near_leg_ticker>\n"
            "Example: /addspread GAZP GZZ4\n"
            "Note: Tickers must be different"
        )
        return

    # Check if user already has an active session
    existing_state = get_state(user_id)
    if existing_state:
        # Replace existing session with new one
        pass  # Will be overwritten below

    # Create initial state
    initial_state = SpreadCreationState(
        user_id=user_id,
        far_leg_ticker=far_leg_ticker,
        near_leg_ticker=near_leg_ticker,
        current_step="ticker_validation",
    )

    # Save state
    save_state(user_id, initial_state.to_dict())

    # Send confirmation message
    await message.answer(
        f"Starting spread creation process:\n"
        f"Far leg: {far_leg_ticker}\n"
        f"Near leg: {near_leg_ticker}\n\n"
        f"Validating tickers..."
    )


async def handle_spread_callback(callback_query: types.CallbackQuery) -> None:
    """
    Handle callback queries from spread creation inline keyboards.

    Routes callback queries to appropriate handlers based on callback data.

    Args:
        callback_query: Telegram callback query from inline keyboard
    """
    await callback_query.answer()

    user_id = callback_query.from_user.id
    callback_data = callback_query.data

    # Parse callback data format: "action:value" or "action:subaction:value"
    parts = callback_data.split(":")
    if len(parts) < 2:
        await callback_query.message.edit_text(
            "❌ Invalid action. Please start over with /addspread"
        )
        return

    action = parts[0]
    value = parts[1] if len(parts) >= 2 else None
    subvalue = parts[2] if len(parts) >= 3 else None

    try:
        if action == "direction":
            await process_direction_callback(callback_query, value)
        elif action == "price":
            await process_price_callback(callback_query, value, subvalue)
        elif action == "amount":
            await process_amount_callback(callback_query, value, subvalue)
        elif action == "confirm":
            await process_confirmation_callback(callback_query, value, subvalue)
        elif action == "action":
            await process_navigation_callback(callback_query, value, subvalue)
        elif action == "info":
            # Info callbacks (like lot info) - just acknowledge
            pass
        else:
            await callback_query.message.edit_text(
                "❌ Unknown action. Please start over with /addspread"
            )
    except Exception as e:
        await callback_query.message.edit_text(
            f"❌ Error processing request: {str(e)}\n"
            f"Please start over with /addspread"
        )


async def process_direction_callback(
    callback_query: types.CallbackQuery, direction: str
) -> None:
    """
    Process direction selection callback.

    Args:
        callback_query: Telegram callback query
        direction: Selected direction ('buy' or 'sell')
    """
    user_id = callback_query.from_user.id
    state = get_state(user_id)

    if not state:
        await callback_query.message.edit_text(
            "❌ Session expired. Please start over with /addspread"
        )
        return

    # Calculate market-neutral prices
    try:
        far_leg_data = state.get("far_leg_data")
        near_leg_data = state.get("near_leg_data")

        if far_leg_data and near_leg_data:
            buy_price, sell_price = calculate_spread_price(
                far_leg_data, near_leg_data, direction
            )
        else:
            # If we don't have price data yet, use placeholder values
            buy_price, sell_price = None, None
    except Exception:
        buy_price, sell_price = None, None

    # Update state with direction and prices
    updates = {"direction": direction, "current_step": "price_input"}

    if buy_price is not None:
        updates["market_neutral_buy_price"] = buy_price
    if sell_price is not None:
        updates["market_neutral_sell_price"] = sell_price

    update_state(user_id, updates)

    # Update message with price selection menu
    updated_state = get_state(user_id)
    message_text = format_price_message(updated_state)
    markup = generate_price_menu(updated_state)

    await callback_query.message.edit_text(
        text=message_text, reply_markup=markup, parse_mode="Markdown"
    )


async def process_price_callback(
    callback_query: types.CallbackQuery, price_type: str, price_value: Optional[str]
) -> None:
    """
    Process price selection callback.

    Args:
        callback_query: Telegram callback query
        price_type: Type of price selection ('market' or 'custom')
        price_value: Price value if market price selected
    """
    user_id = callback_query.from_user.id
    state = get_state(user_id)

    if not state:
        await callback_query.message.edit_text(
            "❌ Session expired. Please start over with /addspread"
        )
        return

    if price_type == "market" and price_value:
        # Use market price
        try:
            price = int(price_value)
            update_state(
                user_id, {"custom_price": price, "current_step": "amount_input"}
            )

            # Update message with amount selection menu
            updated_state = get_state(user_id)
            message_text = format_amount_message(updated_state)
            markup = generate_amount_menu(updated_state)

            await callback_query.message.edit_text(
                text=message_text, reply_markup=markup, parse_mode="Markdown"
            )
        except ValueError:
            await callback_query.message.edit_text(
                "❌ Invalid price format. Please start over with /addspread"
            )

    elif price_type == "custom":
        # Request custom price input
        update_state(user_id, {"current_step": "custom_price_input"})

        await callback_query.message.edit_text(
            "💰 **Custom Price Input**\n\n"
            "Please enter your custom spread price as an integer.\n"
            "Example: 150\n\n"
            "Send your price in the next message:",
            parse_mode="Markdown",
        )


async def process_amount_callback(
    callback_query: types.CallbackQuery, amount_type: str, amount_value: Optional[str]
) -> None:
    """
    Process amount selection callback.

    Args:
        callback_query: Telegram callback query
        amount_type: Type of amount selection ('input')
        amount_value: Amount value if provided
    """
    user_id = callback_query.from_user.id
    state = get_state(user_id)

    if not state:
        await callback_query.message.edit_text(
            "❌ Session expired. Please start over with /addspread"
        )
        return

    if amount_type == "input":
        # Request amount input
        update_state(user_id, {"current_step": "custom_amount_input"})

        await callback_query.message.edit_text(
            "🔢 **Amount Input**\n\n"
            "Please enter the amount you want to trade as a positive integer.\n"
            "This should meet the minimum lot requirements shown earlier.\n\n"
            "Example: 5\n\n"
            "Send your amount in the next message:",
            parse_mode="Markdown",
        )


async def process_confirmation_callback(
    callback_query: types.CallbackQuery, confirm_type: str, confirm_value: Optional[str]
) -> None:
    """
    Process confirmation callback.

    Args:
        callback_query: Telegram callback query
        confirm_type: Type of confirmation ('create')
        confirm_value: Confirmation value if provided
    """
    user_id = callback_query.from_user.id
    state = get_state(user_id)

    if not state:
        await callback_query.message.edit_text(
            "❌ Session expired. Please start over with /addspread"
        )
        return

    if confirm_type == "create":
        # Create the spread
        try:
            result = await create_spread_in_database(state)

            if result.get("success"):
                spread_id = result.get("id")
                await callback_query.message.edit_text(
                    f"✅ **Spread Created Successfully!**\n\n"
                    f"**Spread ID:** {spread_id}\n"
                    f"**Far Leg:** {state.get('far_leg_ticker')}\n"
                    f"**Near Leg:** {state.get('near_leg_ticker')}\n"
                    f"**Direction:** {state.get('direction', '').title()}\n"
                    f"**Price:** {state.get('custom_price')}\n"
                    f"**Amount:** {state.get('amount')}\n\n"
                    f"The spread is now active and available for trading.",
                    parse_mode="Markdown",
                )

                # Clear the session state
                clear_state(user_id)
            else:
                error_msg = result.get("error", "Unknown error")
                await callback_query.message.edit_text(
                    f"❌ **Failed to Create Spread**\n\n"
                    f"Error: {error_msg}\n\n"
                    f"Please try again with /addspread",
                    parse_mode="Markdown",
                )

        except Exception as e:
            await callback_query.message.edit_text(
                f"❌ **Error Creating Spread**\n\n"
                f"Error: {str(e)}\n\n"
                f"Please try again with /addspread",
                parse_mode="Markdown",
            )


async def process_navigation_callback(
    callback_query: types.CallbackQuery, nav_type: str, nav_value: Optional[str]
) -> None:
    """
    Process navigation callback (back, cancel).

    Args:
        callback_query: Telegram callback query
        nav_type: Type of navigation ('back' or 'cancel')
        nav_value: Navigation value if provided
    """
    user_id = callback_query.from_user.id

    if nav_type == "cancel":
        # Cancel the entire process
        clear_state(user_id)
        await callback_query.message.edit_text(
            "❌ **Spread Creation Cancelled**\n\n"
            "You can start over anytime with /addspread",
            parse_mode="Markdown",
        )
        return

    elif nav_type == "back":
        # Go back to previous step
        state = get_state(user_id)
        if not state:
            await callback_query.message.edit_text(
                "❌ Session expired. Please start over with /addspread"
            )
            return

        current_step = state.get("current_step")

        if current_step == "price_input":
            # Go back to direction selection
            update_state(user_id, {"current_step": "direction_selection"})
            updated_state = get_state(user_id)
            message_text = format_direction_message(updated_state)
            markup = generate_direction_menu(updated_state)

        elif current_step == "amount_input":
            # Go back to price selection
            update_state(user_id, {"current_step": "price_input"})
            updated_state = get_state(user_id)
            message_text = format_price_message(updated_state)
            markup = generate_price_menu(updated_state)

        elif current_step == "confirmation":
            # Go back to amount selection
            update_state(user_id, {"current_step": "amount_input"})
            updated_state = get_state(user_id)
            message_text = format_amount_message(updated_state)
            markup = generate_amount_menu(updated_state)

        else:
            # Default: go to direction selection
            update_state(user_id, {"current_step": "direction_selection"})
            updated_state = get_state(user_id)
            message_text = format_direction_message(updated_state)
            markup = generate_direction_menu(updated_state)

        await callback_query.message.edit_text(
            text=message_text, reply_markup=markup, parse_mode="Markdown"
        )


async def create_spread_in_database(state: dict) -> dict:
    """
    Create spread in database using the Django API.

    Args:
        state: Complete spread creation state

    Returns:
        Dictionary with creation result
    """
    try:
        # Prepare spread data for API
        spread_data = {
            "far_leg_figi": state["far_leg_data"]["figi"],
            "near_leg_figi": state["near_leg_data"]["figi"],
            "sell": state["direction"] == "sell",
            "price": state["custom_price"],
            "amount": state["amount"],
        }

        # Add calculated ratio if available
        if "calculated_ratio" in state:
            spread_data["editable_ratio"] = state["calculated_ratio"]

        # Call the API to create spread
        result = await create_spread(spread_data)
        return result

    except Exception as e:
        return {"success": False, "error": str(e)}


# Register callback query handler for spread creation
@dp.callback_query_handler(
    lambda c: c.data
    and (
        c.data.startswith("direction:")
        or c.data.startswith("price:")
        or c.data.startswith("amount:")
        or c.data.startswith("confirm:")
        or c.data.startswith("action:")
        or c.data.startswith("info:")
    ),
    is_me=True,
)
async def spread_callback_handler(callback_query: types.CallbackQuery):
    """Handle spread creation callback queries."""
    await handle_spread_callback(callback_query)


@dp.message_handler(lambda message: (
    message.text and 
    message.text.isdigit() and 
    get_state(message.from_user.id) is not None and
    get_state(message.from_user.id).get('current_step') in ['custom_price_input', 'custom_amount_input']
), is_me=True)
async def handle_custom_input(message: types.Message):
    """
    Handle custom price and amount input from users.

    This handler processes numeric input when users are in custom input steps.
    """
    user_id = message.from_user.id
    state = get_state(user_id)

    if not state:
        return  # No active session, ignore

    current_step = state.get("current_step")

    if current_step == "custom_price_input":
        # Process custom price input
        try:
            price = int(message.text)

            # Validate price (basic validation)
            if price <= 0:
                await message.answer(
                    "❌ Price must be a positive integer. Please try again:"
                )
                return

            # Update state with custom price
            update_state(
                user_id, {"custom_price": price, "current_step": "amount_input"}
            )

            # Show amount selection menu
            updated_state = get_state(user_id)
            message_text = format_amount_message(updated_state)
            markup = generate_amount_menu(updated_state)

            await message.answer(
                text=message_text, reply_markup=markup, parse_mode="Markdown"
            )

        except ValueError:
            await message.answer("❌ Please enter a valid integer price:")

    elif current_step == "custom_amount_input":
        # Process custom amount input
        try:
            amount = int(message.text)

            # Validate amount
            if amount <= 0:
                await message.answer(
                    "❌ Amount must be a positive integer. Please try again:"
                )
                return

            # Check minimum lot requirements
            far_leg_data = state.get("far_leg_data", {})
            near_leg_data = state.get("near_leg_data", {})

            far_lot = far_leg_data.get("lot", 1)
            near_lot = near_leg_data.get("lot", 1)
            min_lot = max(far_lot, near_lot)

            if amount < min_lot:
                await message.answer(
                    f"❌ Amount must be at least {min_lot} (minimum lot requirement). Please try again:"
                )
                return

            # Update state with amount
            update_state(user_id, {"amount": amount, "current_step": "confirmation"})

            # Show confirmation menu
            updated_state = get_state(user_id)
            message_text = format_spread_summary(updated_state)
            markup = generate_confirmation_menu(updated_state)

            await message.answer(
                text=message_text, reply_markup=markup, parse_mode="Markdown"
            )

        except ValueError:
            await message.answer("❌ Please enter a valid integer amount:")
