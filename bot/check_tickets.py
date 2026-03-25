import os
import time
import random
import requests
import logging
from plyer import notification
from playwright.sync_api import sync_playwright

logging.basicConfig(
    filename='ticket_checker.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not set. Skipping notification.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Telegram message sent successfully.")
        logging.info("Telegram message sent successfully.")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
        logging.error(f"Failed to send Telegram message: {e}")

def send_desktop_notification(title, message):
    try:
        notification.notify(
            title=title,
            message=message,
            app_name='Ticket Checker',
            timeout=10
        )
        print("Desktop notification sent.")
        logging.info("Desktop notification sent.")
    except Exception as e:
        print(f"Failed to send desktop notification: {e}")
        logging.error(f"Failed to send desktop notification: {e}")

def check_tickets():
    delay = random.randint(0, 180) # up to 3 minutes
    print(f"Waiting for {delay} seconds before checking to avoid rate limits...")
    logging.info(f"Waiting for {delay} seconds before checking to avoid rate limits...")
    time.sleep(delay)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()

        try:
            print("Checking Paytm/District.in for Hail Mary...")
            logging.info("Checking Paytm/District.in for Hail Mary...")
            url = "https://www.district.in/movies/project-hail-mary-movie-tickets-in-chennai-MV200953"
            page.goto(url, timeout=60000)
            page.wait_for_timeout(5000)

            body_text = page.inner_text("body")

            is_booking_open = False
            message = ""

            if "Filters" in body_text and ("Available" in body_text or "Filling fast" in body_text):
                is_booking_open = True
                message = f"🎟️ **TICKETS ALERT!** 🎟️\nBookings have opened for 'Hail Mary' in Chennai!\n"

            if "Palazzo" in body_text:
                is_booking_open = True
                message = f"🎟️ **PALAZZO TICKETS ALERT!** 🎟️\n'Hail Mary' is now showing at PVR Palazzo!\n"

                if "IMAX" in body_text:
                    message = f"🚀 **PALAZZO IMAX ALERT!** 🚀\n'Hail Mary' IMAX tickets are open at PVR Palazzo!\n"

            if is_booking_open:
                message += f"\nBook your tickets immediately: {url}"
                print(message)
                logging.info(message.replace('\n', ' '))
                send_telegram_message(message)
                send_desktop_notification("Tickets Available!", message)
            else:
                print("Tickets not yet available/bookable for Hail Mary at PVR Palazzo.")
                logging.info("Tickets not yet available/bookable for Hail Mary at PVR Palazzo.")

        except Exception as e:
            print(f"An error occurred while checking: {e}")
            logging.error(f"An error occurred while checking: {e}")
        finally:
            browser.close()

if __name__ == "__main__":
    check_tickets()
