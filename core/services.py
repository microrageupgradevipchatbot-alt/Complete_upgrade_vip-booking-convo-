from langchain.tools import tool
from .config import dev_url, api_key
import requests
from rag_utils.setup import logger
from typing import Optional  # <-- add
#-------------------------------functions---------------------------------------
#=============================transport services function===========================

def get_transport_services(airport_id: str, currency: str) -> dict:
    # Validate currency parameter
    if not currency or currency.strip() == "":
        logger.error("❌ Currency parameter is required for transport services API")
        return {"error": "Currency not specified", "message": "Please select a currency preference first."}
    
    logger.info(f"🚗 Calling Transport services API - airport_id={airport_id}, currency={currency}")
    

    
    endpoint = f"{dev_url}get_vehicles?is_arrival=1&airport_id={airport_id}&currency={currency}"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    try:
        logger.info(f"🌐 Calling Production endpoint: {endpoint}")
        response = requests.get(endpoint, headers=headers, timeout=8)
        response.raise_for_status()
        try:
            result = response.json()
            logger.info(f"✅ Successfully connected to transport services API (Production:{result})")
            # Filter out unnecessary fields from each vehicle card
            filtered_vehicles = []
            for vehicle in result.get("data", []):
                filtered_vehicle = {
                    "name": vehicle.get("name"),
                    "price": vehicle.get("price"),
                    "ten": vehicle.get("ten"),
                    "thirty": vehicle.get("thirty"),
                    "plus": vehicle.get("plus"),
                    "currency": vehicle.get("currency"),
                    "words": vehicle.get("words"),
                    "capacity": vehicle.get("capacity"),
                    "price_mutiple": vehicle.get("price_mutiple"),
                    "org_price": vehicle.get("org_price"),
                }
                filtered_vehicles.append(filtered_vehicle)
            return {
                "code": result.get("code", 1),
                "message": result.get("message", "success"),
                "data": filtered_vehicles
            }
        except Exception as e:
            logger.error(f"❌ Invalid JSON response from Production: {e}")
            return "Invalid Json response "
    except Exception as e:
        logger.error(f"❌ Transport services API request failed: {e}")
        return "Sorry API request for vehicles failed "
def format_transport_services_message(transport_data, flight_data, passenger_count, preferred_currency, arrival_or_departure=None):
    logger.info(f"🚪 Inside Formatting transport services message function")
    vehicles = transport_data.get("data", []) if transport_data else []
    if not vehicles:
        return "Sorry, no transport services are available for your selected flight and requirements."

    
    currency_symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = currency_symbols.get(preferred_currency, "$")

    msg = "Available Transport Services:\n\n"

    for i, vehicle in enumerate(vehicles, 1):
        name = vehicle.get("name", "Transport Service")
        price = vehicle.get("price", 0)
        msg += f"{i}. **Title:** {name}\n"
        msg += f"   **Price:** {symbol}{price}\n"
        msg += f"**Description:**\n"
        words = vehicle.get("words", "")
        if words:
            details = [detail.strip() for detail in words.split(",")]
            for detail in details:
                if detail:
                    msg += f"{detail}\n"
        else:
            msg += "Not specified\n"
        msg += "\n" + "="*50 + "\n\n"

    msg += "Please select a transport service by typing the number (e.g., '1', '2', etc.)"
    logger.info(f"🚗 Formatted transport services message: {msg}")
    return msg

#=============================vip services function===========================

def get_vip_services(airport_id: str, travel_type: str, currency: str, service_id: str = None) -> dict:
    # Validate currency parameter
    if not currency or currency.strip() == "":
        logger.error("❌ Currency parameter is required for VIP services API")
        return {"error": "Currency not specified", "message": "Please select a currency preference first."}
    
    logger.info(f"🛎️ Calling VIP services API - airport_id={airport_id}, travel_type={travel_type}, currency={currency}")
    

    endpoint = f"{dev_url}vip_services?airport_id={airport_id}&travel_type={travel_type}&currency={currency}&service_id={service_id}"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    try:
        logger.info(f"🌐 Calling Production endpoint: {endpoint}")
        response = requests.get(endpoint, headers=headers, timeout=8)
        response.raise_for_status()
        try:
            result = response.json()
            logger.info("✅ Successfully connected to VIP services API (Production)")
            # Filter out unnecessary fields from each service card
            filtered_services = []
            for service in result.get("data", []):
                filtered_service = {
                    "title": service.get("title"),
                    "price": service.get("price"),
                    "currency": service.get("currency"),
                    "airport_name": service.get("airport_name"),
                    "words": service.get("words"),
                    "adults_1": service.get("adults_1"),
                    "adults_2": service.get("adults_2"),
                    "adults_3": service.get("adults_3"),
                    "adults_4": service.get("adults_4"),
                    "adults_5": service.get("adults_5"),
                    "adults_6": service.get("adults_6"),
                    "adults_7": service.get("adults_7"),
                    "adults_8": service.get("adults_8"),
                    "adults_9": service.get("adults_9"),
                    "adults_10": service.get("adults_10"),
                    "refund_text": service.get("refund_text"),
                    "price_mutiple": service.get("price_mutiple"),
                    "meeting_point": service.get("meeting_point"),
                    "cancellation_policy": service.get("cancellation_policy"),
                    "supplierservicename": service.get("supplierservicename"),
                    # Add any other required fields here
                }
                filtered_services.append(filtered_service)
            return {
                "code": result.get("code", 1),
                "message": result.get("message", "success"),
                "data": filtered_services
            }
        except Exception as e:
            logger.error(f"❌ Invalid JSON response from Production: {e}")
            return "Sorry Invalid JSON response from VIP services API"
    except Exception as e:
        logger.error(f"❌ VIP services API request failed: {e}")
        return "Sorry VIP services API request failed"
def format_vip_services_message(vip_data, flight_data, travel_type, passenger_count, preferred_currency):
    logger.info(f"🚪 Inside Formatting vip_services function")
    services = vip_data.get("data", []) if vip_data else []
    if not services:
        return "Sorry, no VIP services are available for your selected flight and requirements."
    
    try:
        passenger_count_int = int(passenger_count) if passenger_count is not None else 0
        if passenger_count_int <= 0:
            return "Invalid passenger count. Please provide a valid number of adults (1-10)."
        if passenger_count_int > 10:
            return "Sorry, we cannot accommodate more than 10 adults. Please enter a number between 1 and 10."
    except (ValueError, TypeError):
        return "Invalid passenger count. Please provide a valid number of adults (1-10)."
    
    currency_symbols = {"USD": "$", "EUR": "€", "GBP": "£"}
    symbol = currency_symbols.get(preferred_currency, "$")
    
    msg = "Available VIP Services:\n\n"
    for i, service in enumerate(services, 1):
        title = service.get("title", "VIP Service")
        price_key = f"adults_{passenger_count}"
        price = service.get(price_key, service.get("price", 0))
        refund_text = service.get("refund_text", "")
        words = service.get("words", "")
        
        msg += f"{i}. Title: **{title}**\n"
        msg += f"   PRICE: {symbol}{price}\n\n"
        
        msg += "**Cancellations and modifications:**\n"
        if refund_text:
            msg += f"  {refund_text}\n\n"
        else:
            msg += "   Not specified\n\n"
        
        msg += "**Description:**\n"
        if words:
            details = [detail.strip() for detail in words.split(",")]
            for detail in details:
                if detail:
                    msg += f"  {detail}\n"
        else:
            msg += "   Not specified\n"
        
        msg += "\n" + "="*50 + "\n\n"
    logger.info(f"✈️ Formatted VIP services message: {msg}")
    msg += "Please select a service by typing the number (e.g., '1', '2', etc.)"
    return msg

#--------------------------------------tools-----------------------------------------
#for vip services
@tool
def vip_services_tool(airport_id: str, travel_type: str, currency: str, service_id: str = None) -> dict:
    """
    Call external API to fetch available Airport VIP services based on flight details and user preferences.

    Parameters:
      airport_id (str): The airport ID from the flight details object.
        - For 'Departure', use the 'origin_airport' field from flight details (e.g., flight_details["origin_airport"]).
        - For 'Arrival', use the 'destination_airport' field from flight details (e.g., flight_details["destination_airport"]).
      travel_type (str): "Arrival" or "Departure" as selected by the user.
      currency (str): User's preferred currency (USD, EUR, GBP).
      service_id (str, optional): keep it null as we are not taking it from user.

    The agent must extract airport_id from the correct field in primary_flight_details or secondary_flight_details,
    depending on whether the user is booking a primary or secondary service, and based on the user's arrival/departure selection.
    """
    return get_vip_services(airport_id, travel_type, currency, service_id)
@tool
def format_vip_services_tool(
    vip_data: Optional[dict] = None,
    flight_data: Optional[dict] = None,
    travel_type: Optional[str] = None,
    passenger_count: Optional[int] = None,
    preferred_currency: Optional[str] = None,
) -> str:
    """Format VIP services into a user-friendly message after calling vip_services_tool."""
    if (
        isinstance(vip_data, dict)
        and "vip_services_tool_response" in vip_data
        and isinstance(vip_data["vip_services_tool_response"], dict)
    ):
        vip_data = vip_data["vip_services_tool_response"]
    # Unwrap flight_data if needed (for consistency)
    if (
        isinstance(flight_data, dict)
        and "flight_details_tool_response" in flight_data
        and isinstance(flight_data["flight_details_tool_response"], dict)
    ):
        flight_data = flight_data["flight_details_tool_response"]
    vip_data = vip_data or {}
    flight_data = flight_data or {}

    # Guardrails for missing essentials
    missing = []
    if travel_type is None:
        missing.append("travel_type")
    if passenger_count is None:
        missing.append("passenger_count")
    if preferred_currency is None:
        missing.append("preferred_currency")
    if missing:
        return "To format VIP services, please provide: " + ", ".join(missing) + "."

    return format_vip_services_message(vip_data, flight_data, travel_type, passenger_count, preferred_currency)

#for transfer services

@tool
def transport_services_tool(airport_id: str, currency: str) -> dict:
    """ Call external API to fetch available transport services for the selected airport and currency.

    Parameters:
      airport_id (str): The airport code. For 'departure', use origin_airport from flight details. For 'arrival', use destination_airport from flight details.
      currency (str): User's preferred currency (USD, EUR, GBP).

    The agent must extract airport_id from the correct field in primary_flight_details or secondary_flight_details,
    depending on whether the user is booking a primary or secondary service, and based on the user's arrival/departure selection.
   """
    return get_transport_services(airport_id, currency)
@tool
def format_transport_services_tool(
    transport_data: Optional[dict] = None,
    flight_data: Optional[dict] = None,
    passenger_count: Optional[int] = None,
    preferred_currency: Optional[str] = None,
    arrival_or_departure: Optional[str] = None,
) -> str:
    """Format transfer services into a user-friendly message after calling transport_services_tool"""
    if (
        isinstance(transport_data, dict)
        and "transport_services_tool_response" in transport_data
        and isinstance(transport_data["transport_services_tool_response"], dict)
    ):
        transport_data = transport_data["transport_services_tool_response"]
    # Unwrap flight_data if needed (for consistency)
    if (
        isinstance(flight_data, dict)
        and "flight_details_tool_response" in flight_data
        and isinstance(flight_data["flight_details_tool_response"], dict)
    ):
        flight_data = flight_data["flight_details_tool_response"]
    
    transport_data = transport_data or {}
    flight_data = flight_data or {}

    missing = []
    if passenger_count is None:
        missing.append("passenger_count")
    if preferred_currency is None:
        missing.append("preferred_currency")
    if missing:
        return "To format transport services, please provide: " + ", ".join(missing) + "."


    
    
    return format_transport_services_message(transport_data, flight_data, passenger_count, preferred_currency, arrival_or_departure)


@tool
def only_vip_services_tool(airport_id: str, travel_type: str, currency: str, passenger_count: int, flight_data: dict = None, service_id: str = None) -> str:
    """
    Fetch and format VIP services in one step.

    Parameters:
      airport_id (str): The airport ID.
      travel_type (str): "Arrival" or "Departure".
      currency (str): User's preferred currency (USD, EUR, GBP).
      passenger_count (int): Number of adults.
      flight_data (dict, optional): Flight details object (can be None).
      service_id (str, optional): Service ID (default None).

    Returns:
      str: Formatted VIP services message.
    """
    vip_data = get_vip_services(airport_id, travel_type, currency, service_id)
    return format_vip_services_message(vip_data, flight_data, travel_type, passenger_count, currency)

@tool
def only_transfer_services_tool(airport_id: str, currency: str, passenger_count: int, flight_data: dict = None, arrival_or_departure: str = None) -> str:
    """
    Fetch and format transfer services in one step.

    Parameters:
      airport_id (str): The airport ID.
      currency (str): User's preferred currency (USD, EUR, GBP).
      passenger_count (int): Number of adults.
      flight_data (dict, optional): Flight details object (can be None).
      arrival_or_departure (str, optional): "Arrival" or "Departure" (default None).

    Returns:
      str: Formatted transfer services message.
    """
    transport_data = get_transport_services(airport_id, currency)
    return format_transport_services_message(transport_data, flight_data, passenger_count, currency, arrival_or_departure)


