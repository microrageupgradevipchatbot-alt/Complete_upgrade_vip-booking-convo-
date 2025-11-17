from langchain.tools import tool

import os
import requests
from rag_utils.setup import logger
#-------------------------------functions---------------------------------------
#=============================transport services function===========================
def get_transport_services(airport_id: str, currency: str) -> dict:
    # Validate currency parameter
    if not currency or currency.strip() == "":
        logger.error("❌ Currency parameter is required for transport services API")
        return {"error": "Currency not specified", "message": "Please select a currency preference first."}
    
    logger.info(f"🚗 Calling Transport services API - airport_id={airport_id}, currency={currency}")
    dev_url = os.getenv("DEV_URL")
    api_key = os.getenv("API_KEY")

    if not dev_url:
        logger.error("❌ No transport services API endpoint configured")
        return {"error": "API configuration missing", "message": "Transport services API endpoint not configured"}

    endpoint = f"{dev_url}get_vehicles?is_arrival=1&airport_id={airport_id}&currency={currency}"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    try:
        logger.info(f"🌐 Calling Production endpoint: {endpoint}")
        response = requests.get(endpoint, headers=headers, timeout=8)
        response.raise_for_status()
        try:
            result = response.json()
            logger.info("✅ Successfully connected to transport services API (Production)")
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
            return {"error": "Invalid JSON response", "message": "Transport services API returned invalid data format"}
    except Exception as e:
        logger.error(f"❌ Transport services API request failed: {e}")
        return {"error": "Request failed", "message": str(e)}
    
def format_transport_services_message(transport_data, flight_data, passenger_count, preferred_currency, arrival_or_departure=None):
    logger.info(f"🚪 Inside Formatting flight choice message function")
    vehicles = transport_data.get("data", []) if transport_data else []
    if not vehicles:
        return "Sorry, no transport services are available for your selected flight and requirements."

    try:
        passenger_count_int = int(passenger_count) if passenger_count is not None else 0
        if passenger_count_int <= 0:
            return "Invalid passenger count. Please provide a valid number of adults (1-10)."
        if passenger_count_int > 10:
            return "Sorry, we cannot accommodate more than 10 adults. Please enter a number between 1 and 10."
    except (ValueError, TypeError):
        return "Invalid passenger count. Please provide a valid number of adults (1-10)."

    flight_info = flight_data.get("data", [{}])[0] if flight_data else {}

    # Determine direction and airport info
    direction = "ARRIVAL"
    airport_name = flight_info.get("destinationName", "")
    flight_date = flight_info.get("date_arrival", "")
    flight_time = f"{flight_info.get('des_hr', '')}:{flight_info.get('des_mn', '')}"

    # Use arrival_or_departure if provided
    if arrival_or_departure is None:
        # Try to get from flight_info or default to "arrival"
        arrival_or_departure = arrival_or_departure.lower()

    if arrival_or_departure == "departure":
        direction = "DEPARTURE"
        airport_name = flight_info.get("originName", "")
        flight_date = flight_info.get("date_departure", "")
        flight_time = f"{flight_info.get('org_hr', '')}:{flight_info.get('org_mn', '')}"

    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£"
    }
    symbol = currency_symbols.get(preferred_currency, "$")

    msg = f"{airport_name}\n{flight_date} {flight_time}\n{direction}\n\n"
    msg += "Available Transport Services:\n\n"

    for i, vehicle in enumerate(vehicles, 1):
        name = vehicle.get("name", "Transport Service")
        price = vehicle.get("price", 0)
        msg += f"{i}. {name}    {symbol}{price}\n\n"
        words = vehicle.get("words", "")
        if words:
            details = [detail.strip() for detail in words.split(",")]
            for detail in details:
                if detail:
                    msg += f"{detail}\n"
        msg += "\n" + "="*50 + "\n\n"

    msg += "Please select a transport service by typing the number (e.g., '1', '2', etc.)"
    return msg

#=============================vip services function===========================
def get_vip_services(airport_id: str, travel_type: str, currency: str, service_id: str = None) -> dict:
    # Validate currency parameter
    if not currency or currency.strip() == "":
        logger.error("❌ Currency parameter is required for VIP services API")
        return {"error": "Currency not specified", "message": "Please select a currency preference first."}
    
    logger.info(f"🛎️ Calling VIP services API - airport_id={airport_id}, travel_type={travel_type}, currency={currency}")
    dev_url = os.getenv("DEV_URL")
    api_key = os.getenv("API_KEY")

    if not dev_url:
        logger.error("❌ No VIP services API endpoint configured")
        return {"error": "API configuration missing", "message": "VIP services API endpoint not configured"}

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
            return {"error": "Invalid JSON response", "message": "VIP services API returned invalid data format"}
    except Exception as e:
        logger.error(f"❌ VIP services API request failed: {e}")
        return {"error": "Request failed", "message": str(e)}

def format_vip_services_message(vip_data, flight_data, travel_type, passenger_count, preferred_currency):
    logger.info(f"🚪 Inside Formatting vip_services function")
    logger.info(f"pessenger_count: {passenger_count}")
    # Check for services in 'data' field (actual API response format)
    services = vip_data.get("data", []) if vip_data else []
    if not services:
        return "Sorry, no VIP services are available for your selected flight and requirements."
    
    # Validate passenger count
    try:
        passenger_count_int = int(passenger_count) if passenger_count is not None else 0
        if passenger_count_int <= 0:
            return "Invalid passenger count. Please provide a valid number of adults (1-10)."
        
        if passenger_count_int > 10:
            return "Sorry, we cannot accommodate more than 10 adults. Please enter a number between 1 and 10."
    except (ValueError, TypeError):
        return "Invalid passenger count. Please provide a valid number of adults (1-10)."
    
    # Get flight info for header
    flight_info = flight_data.get("data", [{}])[0] if flight_data else {}
    airport_name = flight_info.get("originName", "") if travel_type == "Departure" else flight_info.get("destinationName", "")
    flight_date = flight_info.get("date_departure", "") if travel_type == "Departure" else flight_info.get("date_arrival", "")
    flight_time = f"{flight_info.get('org_hr', '')}:{flight_info.get('org_mn', '')}" if travel_type == "Departure" else f"{flight_info.get('des_hr', '')}:{flight_info.get('des_mn', '')}"
    
    # Currency symbols
    currency_symbols = {
        "USD": "$",
        "EUR": "€", 
        "GBP": "£"
    }
    symbol = currency_symbols.get(preferred_currency, "$")
    
    # Build header
    msg = f"{airport_name}\n{flight_date} {flight_time}\n{travel_type.upper()}\n\n"
    msg += "Available VIP Services:\n\n"
    
    # Format each service
    for i, service in enumerate(services, 1):
        title = service.get("title", "VIP Service")
        
        # Get price based on passenger count
        price_key = f"adults_{passenger_count}"
        price = service.get(price_key, service.get("price", 0))
        
        msg += f"{i}. {title}\n"
        msg += f"PRICE: {symbol}{price}\n\n"
        
        # Cancellation policy
        refund_text = service.get("refund_text", "")
        if refund_text:
            msg += f"Cancellations and modifications: {refund_text}\n\n"
        
        # Parse and format service details from 'words' field
        words = service.get("words", "")
        if words:
            # Split by comma and format each detail
            details = [detail.strip() for detail in words.split(",")]
            for detail in details:
                if detail:
                    msg += f"{detail}\n"
        
        msg += "\n" + "="*50 + "\n\n"
    
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
def format_vip_services_tool(vip_data, flight_data, travel_type, passenger_count, preferred_currency) -> str:
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
def format_transport_services_tool(transport_data, flight_data, passenger_count, preferred_currency, arrival_or_departure=None) -> str:
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
    return format_transport_services_message(transport_data, flight_data, passenger_count, preferred_currency, arrival_or_departure)




