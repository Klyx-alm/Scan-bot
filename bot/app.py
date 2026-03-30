import os
import re
import json
import subprocess
import logging
import sys
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bcrypt
import webbrowser
import threading
from knowledge import HackerBot

load_dotenv()

# ---------------- PATH FIX (PYINSTALLER) ----------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# 🔥 IMPORTANT : corriger Flask pour PyInstaller
template_dir = resource_path("bot/templates")

app = Flask(__name__, template_folder=template_dir)
app.secret_key = os.urandom(24)

limiter = Limiter(app=app, key_func=get_remote_address)

# ---------------- USER FILE (WRITE SAFE) ----------------
USER_FILE = os.path.expanduser("~/scanbot_users.json")

if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

with open(USER_FILE, 'r') as f:
    users = json.load(f)

# ---------------- Logging ----------------
logging.basicConfig(filename=os.path.expanduser("~/scanbot.log"),
                    level=logging.INFO,
                    format='%(asctime)s - %(message)s')

bot = HackerBot()

scan_results = {}
scan_history = []

def save_users():
    with open(USER_FILE, 'w') as f:
        json.dump(users, f)

def is_valid_ip(ip):
    return re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip)

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not password or not confirm_password:
            flash("Password is required")
            return redirect("/register")

        if password != confirm_password:
            flash("Passwords do not match")
            return redirect("/register")

        if username in users:
            flash("User already exists")
            return redirect("/register")

        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users[username] = {"password": hashed.decode('latin1'), "theme": "dark"}
        save_users()

        logging.info(f"New user registered: {username}")
        flash("Account created, please login")
        return redirect("/")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if "user" in session:
        return redirect("/dashboard")

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if not password:
            flash("Password is required")
            return redirect("/")

        if username in users and bcrypt.checkpw(password.encode('utf-8'), users[username]["password"].encode('latin1')):
            session["user"] = username
            logging.info(f"User logged in: {username}")
            return redirect("/dashboard")

        flash("Invalid credentials")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    user = session["user"]
    theme = users[user]["theme"]
    return render_template("dashboard.html", scans=scan_results, theme=theme, history=scan_history)

# ---------------- SCAN ----------------
@app.route("/scan", methods=["POST"])
@limiter.limit("5 per minute")
def scan():
    if "user" not in session:
        return redirect("/")
    ip = request.form.get("ip") or ""

    if not is_valid_ip(ip):
        flash("Invalid IP")
        return redirect("/dashboard")

    scan_results[ip] = {"scan": bot.scan(ip)}

    if ip not in scan_history:
        scan_history.append(ip)

    logging.info(f"Scan performed by {session['user']} on {ip}")
    flash("Quick scan completed!")
    return redirect(url_for("dashboard"))

# ---------------- AUTRES ROUTES (inchangées) ----------------
@app.route("/deep", methods=["POST"])
def deep():
    ip = request.form.get("ip") or ""
    if not is_valid_ip(ip):
        return "Invalid IP"
    if ip not in scan_results:
        scan_results[ip] = {}
    scan_results[ip]["deep"] = bot.deep_scan(ip)
    return redirect(url_for("dashboard"))

@app.route("/os", methods=["POST"])
def os_detect():
    ip = request.form.get("ip") or ""
    if not is_valid_ip(ip):
        return "Invalid IP"
    if ip not in scan_results:
        scan_results[ip] = {}
    scan_results[ip]["os"] = bot.detect_os(ip)
    return redirect(url_for("dashboard"))

@app.route("/ports", methods=["POST"])
def ports():
    ip = request.form.get("ip") or ""
    if not is_valid_ip(ip):
        return "Invalid IP"
    if ip not in scan_results:
        scan_results[ip] = {}
    scan_results[ip]["ports"] = bot.port_scan(ip)
    return redirect(url_for("dashboard"))

@app.route("/analyze", methods=["POST"])
def analyze():
    ip = request.form.get("ip") or ""
    if not is_valid_ip(ip):
        flash("Invalid IP")
        return redirect("/dashboard")

    if ip not in scan_results:
        flash("No scan available for this IP.")
        return redirect("/dashboard")

    scan_data = scan_results[ip].get("deep") or scan_results[ip].get("scan", "")
    result = bot.analyze_scan(scan_data)
    scan_results[ip]["analysis"] = result

    flash("Analysis completed!")
    return redirect("/dashboard")

@app.route("/toggle_theme", methods=["POST"])
def toggle_theme():
    if "user" in session:
        user = session["user"]
        users[user]["theme"] = "light" if users[user]["theme"] == "dark" else "dark"
        save_users()
    return "", 200

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    response = bot.chat(message)
    return jsonify({"response": response})

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# ---------------- RUN ----------------
def open_browser():
    webbrowser.open("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(2, open_browser).start()
    app.run(host="127.0.0.1", port=5000, debug=False)
    