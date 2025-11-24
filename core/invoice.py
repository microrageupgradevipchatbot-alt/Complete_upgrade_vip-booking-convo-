from rag_utils.setup import logger

from langchain.tools import tool
from email.mime.text import MIMEText
import smtplib
#----------------------------functions-------------------------------
#==========================invoice==================================
def generate_single_invoice(extracted_info):
    logger.info(f"🚪 Inside single generate invoice function {extracted_info}")
    

    interest = extracted_info.get("primary_interested", "").strip().lower()

    # --- Required fields ---
    base_required_fields = [
        "primary_flight_number", "primary_flight_date", "primary_flight_details",
        "primary_service_selected", "primary_passenger_count",
        "primary_preferred_time", "primary_msg_for_steward", "primary_email"
    ]

    if interest == "vip":
        required_fields = base_required_fields + [
            "primary_Arrival_or_departure", "primary_flight_class",
            "primary_luggage_count", "primary_get_services"
        ]
    elif interest == "transfer":
        required_fields = base_required_fields + [
            "primary_airport_transfer_details", "primary_address"
        ]
    else:
        logger.error(f"❌ Unknown primary service type '{interest}'")
        return None

    for field in required_fields:
        if not extracted_info.get(field):
            logger.error(f"❌ Missing required field '{field}' for service type '{interest}'")
            return None

    logger.info("✅ All required fields present for invoice generation")

    # --- Flight info ---
    
# ...existing code...
    flight_details = extracted_info.get("primary_flight_details", {}) or {}
    # FIX: Unwrap if nested under 'flight_details_tool_response'
    if isinstance(flight_details, dict) and "flight_details_tool_response" in flight_details:
        flight_details = flight_details["flight_details_tool_response"]
    flight_data = (flight_details.get("data") or [{}])[0]
# ...existing code...


    # --- Service list ---
    

    service_selected = extracted_info.get("primary_service_selected", "")
    services_data = []
    interest = extracted_info.get("primary_interested", "").strip().lower()
    # ...existing code...
    if interest == "vip":
        vip_data = extracted_info.get("primary_get_services", {})
        # Unwrap if nested under 'vip_services_tool_response'
        if isinstance(vip_data, dict) and "vip_services_tool_response" in vip_data:
            vip_data = vip_data["vip_services_tool_response"]
        services_data = vip_data.get("data", [])
        service_name_fallback = "Airport VIP Service"
        service_key = "title"
    else:
        transfer_data = extracted_info.get("primary_airport_transfer_details", {})
        # Unwrap if nested under 'transport_services_tool_response'
        if isinstance(transfer_data, dict) and "transport_services_tool_response" in transfer_data:
            transfer_data = transfer_data["transport_services_tool_response"]
        services_data = transfer_data.get("data", [])
        service_name_fallback = "Transport Service"
        service_key = "name"
    # ...existing code...

    service_name, service_words, service_refund = service_name_fallback, "", "usually 48 hours"
    selected_service = None

    if isinstance(service_selected, dict):
        selected_service = service_selected
    elif str(service_selected).strip():
        sel = str(service_selected).strip()
        if sel.isdigit():
            idx = int(sel) - 1
            if 0 <= idx < len(services_data):
                selected_service = services_data[idx]
        else:
            # FIX: Match by checking if the selection is a substring of the service name
            selected_service = next(
                (s for s in services_data 
                 if s.get(service_key) and sel.lower() in s.get(service_key, "").lower()), 
                None
            )
    if selected_service:
        service_name = selected_service.get(service_key, service_name_fallback)
        # FIX: Clean the service name (remove class/descriptors)
        if interest == "transfer":
            # Apply same cleaning logic as format_transport_services_message
            if "(" in service_name and ")" in service_name and service_name.find("(") < service_name.find(")"):
                service_name = service_name[:service_name.find(")") + 1].strip()
            else:
                for sep in [" - ", ", or similar", ", or", ", similar", ","]:
                    if sep in service_name:
                        service_name = service_name.split(sep)[0].strip()
                        break
        service_words = selected_service.get("words", "")
        service_refund = selected_service.get("refund_text", service_refund)

    # --- Travel info ---
    travel_type = extracted_info.get("primary_Arrival_or_departure", "").lower()
    if interest == "vip":
        if travel_type == "departure":
            route_display, code, time, name = (
                "Departure",
                flight_data.get("origin_iata_code", ""),
                f"{flight_data.get('origin_time', '')}",
                flight_data.get("originName", ""),
            )
        else:  # arrival by default
            route_display, code, time, name = (
                "Arrival",
                flight_data.get("destination_iata_code", ""),
                f"{flight_data.get('destination_time', '')}",
                flight_data.get("destinationName", ""),
            )
    elif interest == "transfer":
        if travel_type == "departure":
            route_display, code, time, name = (
                "Departure",
                flight_data.get("origin_iata_code", ""),
                f"{flight_data.get('origin_time', '')}",
                flight_data.get("originName", ""),
            )
        else:  # arrival by default
            route_display, code, time, name = (
                "Arrival",
                flight_data.get("destination_iata_code", ""),
                f"{flight_data.get('destination_time', '')}",
                flight_data.get("destinationName", ""),
            )
    # --- Currency + price ---
    currency = extracted_info.get("primary_preferred_currency")
    symbol = "$" if currency == "USD" else "€" if currency == "EUR" else "£"
    price = extracted_info.get("primary_price")

    logger.info(f"💰 Service price: {symbol}{price} {currency}")

    # --- Build invoice ---
    if interest == "vip":
        invoice = f"""<h2><b>BOOKING INVOICE - UpgradeVIP Services</b></h2>
<br>
<b>Flight Information:</b>
- Flight: {extracted_info.get('primary_flight_number')} on {extracted_info.get('primary_flight_date')}
- {route_display}:
  {code}
  {time}
  {name}
<br><b> Service Type:</b> {service_name}

<br><b>Service Details:</b>
- Adults: {extracted_info.get('primary_passenger_count')}
- Luggage: {extracted_info.get('primary_luggage_count')} pieces
- Meeting Time: {extracted_info.get('primary_preferred_time')}
- Special Instructions: {extracted_info.get('primary_msg_for_steward')}

<br><b>Payment Summary:</b>
- Service Price: {symbol}{price} {currency}
- Total Amount: {symbol}{price} {currency}

<br><b>Contact Information:</b>
- Email: {extracted_info.get('primary_email')}

<br><b>Description:</b>
- {service_words}

<br><b>Important Notes:</b>
- Service refund policy: {service_refund}
- Please arrive 15 minutes before scheduled meeting time
"""
    else:  # transfer

        invoice = f"""<h2><b>BOOKING INVOICE - UpgradeVIP Transport Services</b></h2>

<b>Flight Information:</b>
<br>- Flight: {extracted_info.get('primary_flight_number')} on {extracted_info.get('primary_flight_date')}
- {route_display}:
  {code}
  {time}
  {name}
<br><b> Service Type:</b> {service_name}

<br><b>Transport Details:</b>
- Adults: {extracted_info.get('primary_passenger_count')}
- Pickup/Drop-off Address: {extracted_info.get('primary_address')}
- Pickup Time: {extracted_info.get('primary_preferred_time')}
- Special Instructions: {extracted_info.get('primary_msg_for_steward')}

<br><b>Payment Summary:</b>
- Service Price: {symbol}{price} {currency}
- Total Amount: {symbol}{price} {currency}

<br><b>Contact Information:</b>
- Email: {extracted_info.get('primary_email')}

<br><b>Description:</b>
- {service_words}

"""

    logger.info("🎉 Invoice generated successfully!")
    logger.info(f"📄 Invoice preview: {invoice}...")
    return invoice

def generate_combined_invoice(extracted_info):
   

    logger.info("🧾 Starting combined invoice generation...")

    # --- Generate primary invoice ---
    invoice_primary = generate_single_invoice(extracted_info)

    # --- Generate secondary invoice (only if exists) ---
    invoice_secondary = None
    if extracted_info.get("secondary_interested"):
        # Temporarily map secondary_* fields into primary_* format
        secondary_info = {
            k.replace("secondary_", "primary_"): v
            for k, v in extracted_info.items()
            if k.startswith("secondary_")
        }
        invoice_secondary = generate_single_invoice(secondary_info)

    # --- Prices & Currencies ---
    price_1 = extracted_info.get("primary_price") 
    currency_1 = extracted_info.get("primary_preferred_currency")

    price_2 = extracted_info.get("secondary_price") 
    currency_2 = extracted_info.get("secondary_preferred_currency")

    # Currency symbols
    def get_symbol(cur):
        return "$" if cur == "USD" else "€" if cur == "EUR" else "£"

    symbol_1 = get_symbol(currency_1)
    symbol_2 = get_symbol(currency_2)

    # --- Total logic ---
    if invoice_secondary:
        if currency_1 == currency_2:
            total = price_1 + price_2
            total_line = f"<b>TOTAL FOR BOTH SERVICES:</b> {get_symbol(currency_1)}{total} {currency_1}"
        else:
            total_line = (
                f"<b>Service 1:</b> {symbol_1}{price_1} {currency_1}\n"
                f"<b>Service 2:</b> {symbol_2}{price_2} {currency_2}"
            )

        combined_invoice = (
            f"{invoice_primary}\n\n--- SECONDARY BOOKING ---\n\n"
            f"{invoice_secondary}\n\n"
            f"{total_line}\n"
            
        )
    else:
        combined_invoice = invoice_primary

    logger.info("🎉 Combined invoice generated successfully!")
    return combined_invoice

#==========================email sending function==================================

def send_email(to_email, subject, message):
    logger.info(f"🚪 Inside send email function")
    
    # Replace with your SMTP server details
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "hamzaaakm214@gmail.com"  # Replace with your Gmail address
    smtp_pass = "bphr enas cxxu vkbv"     # Replace with your Gmail app password

    msg = MIMEText(message,'html')
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = to_email

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [to_email], msg.as_string())
        server.quit()
        logger.info(f"✔️🎊Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

#--------------------------tools------------------------------
#for invoice
@tool
def single_generate_invoice_tool(extracted_info: dict) -> str:
    """Generate invoice for one service selected.

    extracted_info must be a dict with keys exactly:
    primary_interested(airport vip ->"vip" , airport transfer->"transfer"), primary_flight_number, primary_flight_date, primary_flight_details,
    primary_service_selected, primary_passenger_count, primary_preferred_time,
    primary_msg_for_steward, primary_email, primary_price, primary_preferred_currency,
    primary_luggage_count, primary_flight_class, primary_Arrival_or_departure,
    primary_get_services (for VIP) OR primary_airport_transfer_details and primary_address (for Transfer).
     
    """

    logger.info(f"🔎Extracted info passed to invoice tool: {extracted_info}")
    return generate_single_invoice(extracted_info)

@tool
def generate_combined_invoice_tool(extracted_info: dict) -> str:
    """Generate combined invoice for both services selected.

    extracted_info must be a dict with keys exactly:
    primary_interested, primary_flight_number, primary_flight_date, primary_flight_details,
    primary_service_selected, primary_passenger_count, primary_preferred_time,
    primary_msg_for_steward, primary_email, primary_price, primary_preferred_currency,
    primary_luggage_count, primary_flight_class, primary_Arrival_or_departure,
    primary_get_services (for VIP) OR primary_airport_transfer_details and primary_address (for Transfer).
    
    secondary_interested, secondary_flight_number, secondary_flight_date, secondary_flight_details,
    secondary_service_selected, secondary_passenger_count, secondary_preferred_time,
    secondary_msg_for_steward, secondary_email, secondary_price, secondary_preferred_currency,
    secondary_luggage_count, secondary_flight_class, secondary_Arrival_or_departure,
    secondary_get_services (for VIP) OR secondary_airport_transfer_details and secondary_address (for Transfer).

    """
    logger.info(f"Extracted info passed to combined invoice tool: {extracted_info}")
    return generate_combined_invoice(extracted_info)

#send email tool
@tool
def send_email_tool(to_email: str, subject: str, message: str) -> bool:
    """
    Send booking/invoice email to the user.

    Parameters:
      to_email (str): Recipient email address.
      subject (str): Email subject (e.g. "Your UpgradeVIP Booking Invoice").
      message (str): Email body (HTML or plain text).

    Returns:
      bool: True if email was sent successfully, False otherwise.
    """
    return send_email(to_email, subject, message)
