import os
import re
import json
import subprocess
import logging
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import bcrypt
from knowledge import HackerBot

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

limiter = Limiter(app=app, key_func=get_remote_address)

# Logging
logging.basicConfig(filename='scanbot.log', level=logging.INFO, format='%(asctime)s - %(message)s')

bot = HackerBot()

# Load users
with open('bot/users.json', 'r') as f:
    users = json.load(f)

scan_results = {}
scan_history = []


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
        with open('bot/users.json', 'w') as f:
            json.dump(users, f)
        logging.info(f"New user registered: {username}")
        flash("Account created, please login")
        return redirect("/")
    return '''<!DOCTYPE html>
<html>
<head>
<title>Scan Bot Register</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body{
background:#020617;
color:white;
}
.card{
background:#0f172a;
padding:20px;
border-radius:10px;
}
.form-control {
background:#1e293b;
border:1px solid #334155;
color:white;
}
.btn {
background:#dc2626;
border:none;
}
.btn:hover {
background:#b91c1c;
}
</style>
</head>
<body>
<div class="container mt-5">
<div class="row justify-content-center">
<div class="col-md-4">
<div class="card">
<h3 class="text-center mb-4">📝 Scan Bot Register</h3>
<form method="post">
<input name="username" class="form-control mb-3" placeholder="Username" required>
<input name="password" type="password" class="form-control mb-3" placeholder="Password" required>
<input name="confirm_password" type="password" class="form-control mb-3" placeholder="Confirm Password" required>
<button class="btn w-100">Register</button>
</form>
<p class="text-center mt-3"><a href="/" style="color:#60a5fa;">Already have an account? Login</a></p>
</div>
</div>
</div>
</div>
</body>
</html>'''
def is_valid_ip(ip):
    return re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip)


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
            return
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
    welcome = bot.get_welcome()
    return render_template("dashboard.html", scans=scan_results, theme=theme, history=scan_history, welcome=welcome)


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


# ---------------- DEEP ----------------
@app.route("/deep", methods=["POST"])
def deep():

    ip = request.form.get("ip") or ""

    if not is_valid_ip(ip):
        return "Invalid IP"

    if ip not in scan_results:
        scan_results[ip] = {}

    scan_results[ip]["deep"] = bot.deep_scan(ip)

    return redirect(url_for("dashboard"))


# ---------------- OS ----------------
@app.route("/os", methods=["POST"])
def os_detect():

    ip = request.form.get("ip") or ""

    if not is_valid_ip(ip):
        return "Invalid IP"

    if ip not in scan_results:
        scan_results[ip] = {}

    scan_results[ip]["os"] = bot.detect_os(ip)

    return redirect(url_for("dashboard"))


# ---------------- PORT SCAN ----------------
@app.route("/ports", methods=["POST"])
def ports():

    ip = request.form.get("ip") or ""

    if not is_valid_ip(ip):
        return "Invalid IP"

    if ip not in scan_results:
        scan_results[ip] = {}

    scan_results[ip]["ports"] = bot.port_scan(ip)

    return redirect(url_for("dashboard"))


# ---------------- ANALYZE ----------------
@app.route("/analyze", methods=["POST"])
def analyze():

    ip = request.form.get("ip") or ""

    if not is_valid_ip(ip):
        flash("Invalid IP")
        return redirect("/dashboard")

    if ip not in scan_results:
        flash("No scan available for this IP. Please run a scan first.")
        return redirect("/dashboard")

    # 🔥 prend deep scan en priorité
    scan_data = scan_results[ip].get("deep") or scan_results[ip].get("scan", "")

    result = bot.analyze_scan(scan_data)

    scan_results[ip]["analysis"] = result

    flash("Analysis completed!")
    return redirect("/dashboard")

# ---------------- TOGGLE THEME ----------------
@app.route("/toggle_theme", methods=["POST"])
def toggle_theme():
    if "user" in session:
        user = session["user"]
        users[user]["theme"] = "light" if users[user]["theme"] == "dark" else "dark"
        with open('bot/users.json', 'w') as f:
            json.dump(users, f)
    return "", 200
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "")
    response = bot.chat(message)
    return jsonify({"response": response})


# ---------------- NIKTO ----------------
@app.route("/nikto", methods=["POST"])
def nikto():
    ip = request.form.get("ip") or ""
    if not is_valid_ip(ip):
        flash("Invalid IP")
        return redirect("/dashboard")
    if ip not in scan_results:
        scan_results[ip] = {}
    try:
        proc = subprocess.run(["/usr/local/bin/nikto", "-h", f"http://{ip}"], capture_output=True, text=True, timeout=60)
        if proc.returncode == 0:
            scan_results[ip]["nikto"] = proc.stdout
            flash("Nikto scan completed!")
        else:
            output = proc.stdout + proc.stderr
            if output.strip():
                scan_results[ip]["nikto"] = f"Nikto output:\n{output}"
                flash("Nikto scan completed (check output for issues)")
            else:
                scan_results[ip]["nikto"] = f"❌ Nikto error: Exit code {proc.returncode}"
                flash(f"Nikto error: Exit code {proc.returncode}")
    except subprocess.TimeoutExpired:
        scan_results[ip]["nikto"] = "❌ Nikto scan timed out. No web server found on port 80/443."
        flash("Nikto scan timed out")
    except Exception as e:
        scan_results[ip]["nikto"] = f"❌ ERROR: {str(e)}"
        flash(f"Nikto error: {str(e)}")
    return redirect("/dashboard")

# ---------------- GOBUSTER ----------------
@app.route("/gobuster", methods=["POST"])
def gobuster():
    ip = request.form.get("ip") or ""
    wordlist = request.form.get("wordlist", os.path.expanduser("~/seclists/Discovery/Web-Content/common.txt"))
    wordlist = os.path.expanduser(wordlist)
    if not is_valid_ip(ip):
        flash("Invalid IP")
        return redirect("/dashboard")
    if ip not in scan_results:
        scan_results[ip] = {}
    try:
        if not os.path.exists(wordlist):
            msg = f"❌ Wordlist not found: {wordlist}\n\nDownload wordlists: git clone https://github.com/danielmiessler/SecLists.git ~/seclists\nThen use: ~/seclists/Discovery/Web-Content/common.txt"
            scan_results[ip]["gobuster"] = msg
            flash("Wordlist not found!")
            return redirect("/dashboard")
        proc = subprocess.run(["/usr/local/bin/gobuster", "dir", "-u", f"http://{ip}", "-w", wordlist], capture_output=True, text=True, timeout=120)
        if proc.returncode == 0:
            scan_results[ip]["gobuster"] = proc.stdout
            flash("Gobuster scan completed!")
        else:
            output = proc.stdout + proc.stderr
            if output.strip():
                scan_results[ip]["gobuster"] = f"Gobuster output:\n{output}"
                flash("Gobuster scan completed (no directories found or error)")
            else:
                scan_results[ip]["gobuster"] = f"❌ Gobuster error: Exit code {proc.returncode}"
                flash(f"Gobuster error: Exit code {proc.returncode}")
    except subprocess.TimeoutExpired:
        scan_results[ip]["gobuster"] = "❌ Gobuster scan timed out. Try with a smaller wordlist."
        flash("Gobuster scan timed out")
    except Exception as e:
        scan_results[ip]["gobuster"] = f"❌ ERROR: {str(e)}"
        flash(f"Gobuster error: {str(e)}")
    return redirect("/dashboard")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)