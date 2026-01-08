from rag_utils.setup import logger
import os
from .config import dev_url, api_key
import requests
from langchain.tools import tool
from .services import get_vip_services, get_transport_services
#-------------------------------functions---------------------------------------
#=============================flight details function===========================
def get_flight_details_from_api(flight_number: str, flight_date: str) -> dict:
    logger.info(f"🛫 Calling flight details API with parameters:")
    logger.info(f"   - Flight Number: {flight_number}")
    logger.info(f"   - Flight Date: {flight_date}")
    

    endpoint = f"{dev_url}get_flight_details?flight_number={flight_number}&flightdate={flight_date}"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    try:
        logger.info(f"🌐 Calling Production endpoint: {endpoint}")
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        try:
            result = response.json()
            logger.info(f"✅ Successfully connected to flight details API (Production) : {result}")
            # Filter only required fields
            filtered_flights = []
            for flight in result.get("data", []):
                filtered_flight = {
                    "origin_iata_code": flight.get("origin_iata_code"),#"TLV",
                    "originName": flight.get("originName"),#Ben Gurion Airport TLV
                    "origin_airport": flight.get("origin_airport"),
                    "origin_time":flight.get("origin_time"),
                    "destination_iata_code": flight.get("destination_iata_code"),
                    "destinationName": flight.get("destinationName"),
                    "destination_airport": flight.get("destination_airport"),
                    "destination_time": flight.get("destination_time"),
                    "date_departure": flight.get("date_departure"),
                    "date_arrival": flight.get("date_arrival"),
                 
                }
                filtered_flights.append(filtered_flight)
            return {
                "code": result.get("code", 1),
                "message": result.get("message", "success"),
                "data": filtered_flights
            }
        except Exception as e:
            logger.error(f"❌ Invalid JSON response from Production: {e}")
            return {"error": "Invalid JSON response", "message": "API returned invalid data format"}
    except Exception as e:
        return {"error": "Request failed", "message": str(e)}  
def format_flight_choice_message_impl(flight_data: dict) -> str:
    logger.info(f"🚪 Inside Formatting flight choice message function")
    if not flight_data or "data" not in flight_data or not flight_data["data"]:
        return "Sorry, flight details could not be retrieved make sure your flight number is correct and date is in MM/DD/YYYY format like 10/29/2025."
    info = flight_data["data"][0]
    msg = (
        f"**Departure:**\n"
        f"{info.get('origin_iata_code', '')}    {info.get('origin_time', '')}\n"
        f"{info.get('date_departure', '')}\n"
        f"{info.get('originName', '')}\n\n"
        f"**Arrival:**\n"
        f"{info.get('destination_iata_code', '')}    {info.get('destination_time', '')}\n"
        f"{info.get('date_arrival', '')}\n"
        f"{info.get('destinationName', '')}\n\n"
        f"Which do you want to choose: arrival or departure?"
    )
    logger.info(f"✈️ Formatted flight choice message: {msg}")
    return msg

#=============================airports list function===========================
def get_airports_from_api() -> dict:
    """
    Fetch airports list from external API and return only id and airport_name for each entry.
    """
    endpoint = f"{dev_url}get_airports"
    headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    try:
        logger.info(f"🌐 Calling airports endpoint: {endpoint}")
        response = requests.get(endpoint, headers=headers, timeout=10)
        response.raise_for_status()
        try:
            result = response.json()
            logger.info(f"🔗 Successfully connected to airports API: {result}")

            # Filter only id and airport_name for each airport
            filtered_airports = []
            for airport in result.get("data", []):
                filtered_airports.append({
                    "id": airport.get("id", ""),
                    "airport_name": airport.get("airport_name", "")
                })
            
            logger.info(f"✂️ After trimming : {filtered_airports}")
            return {
                "code": result.get("code", 1),
                "message": result.get("message", "success"),
                "data": filtered_airports
            }
        except Exception as e:
            logger.error(f"❌ Invalid JSON response from airports API: {e}")
            return {"error": "Invalid JSON response", "message": "API returned invalid data format"}
    except Exception as e:
        logger.error(f"❌ Airports API request failed: {e}")
        return {"error": "Request failed", "message": str(e)}
def format_airports_message(airports_data: dict) -> str:
    logger.info(f"🚪 Inside Formatting airports message function")
    if not airports_data or "data" not in airports_data or not airports_data["data"]:
        return "Sorry, airport list could not be retrieved."
    return "\n".join(f"{i+1}) {a['airport_name']}" for i, a in enumerate(airports_data["data"]))

#=============================tools===========================
#for airports list
@tool
def airports_tool():
    """Fetch and format airport list for user selection."""
    airports_data = get_airports_from_api()
    return format_airports_message(airports_data)
@tool
def airports_raw_tool() -> dict:
    """
    Fetch the raw airport list from the external API.
    Returns the full JSON/dict response from get_airports_from_api().
    """
    return get_airports_from_api()
#for flight details
@tool
def flight_details_tool(flight_number: str, flight_date: str):
    """
    Call external API to fetch flight details.

    Parameters:
      flight_number (str): The user's flight number (e.g., 'LY001').
      flight_date (str): The user's flight date (e.g., '11/31/2025' in mm/dd/yyyy format).

    Call this tool as soon as both flight number and flight date are provided by the user.
    """
    return get_flight_details_from_api(flight_number, flight_date)

@tool
def format_flight_choice_tool(flight_data: dict) -> str:
    """Format flight details into a user-friendly message after calling flight_details_tool."""
    # Unwrap if the LLM nested it or sent a single object instead of {data:[...]}
    if isinstance(flight_data, dict) and "flight_details_tool_response" in flight_data:
        flight_data = flight_data["flight_details_tool_response"]
    # If the LLM sent a single-flight dict, wrap it as {data: [dict]}
    if isinstance(flight_data, dict) and "data" not in flight_data and "flight_no" in flight_data:
        flight_data = {"data": [flight_data]}
    return format_flight_choice_message_impl(flight_data)

#=============================Get Services by Airport Name===========================

