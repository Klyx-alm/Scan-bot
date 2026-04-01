## ScanBot (Mac version disponible)

ScanBot est un outil de cybersécurité permettant d’analyser des machines via leur adresse IP grâce à une interface web moderne et un assistant IA intégré.

🔥 Fonctionnalités
🔍 Scan rapide
🧠 Deep scan (scan approfondi)
🖥️ Détection du système (OS)
⚠️ Analyse intelligente des vulnérabilités
📂 Bruteforce de répertoires (Gobuster)
🤖 Chat IA intégré
## ⚠️ Important

La détection du système (OS) nécessite des privilèges administrateur.

Mac / Linux :
sudo ./ScanBot
Windows :
Lancer ScanBot en tant qu’administrateur dans le terminal

## Téléchargement
SOLUTION 1 (LA PLUS SIMPLE)

## Pour télécharger ton .zip, utilise :
```bash
curl -L -o scanbot.zip https://github.com/Klyx-alm/Scan-bot/archive/refs/tags/v1.1.zip

Puis :
unzip scanbot.zip

cd Scan-bot-1.1

SOLUTION 2 (Vraiment simple)

Aller sur :
👉 https://github.com/Klyx-alm/Scan-bot/releases

Télécharger ScanBot.zip

Décompresser le fichier

Double-cliquer sur ScanBot (aucune installation requise)

⚙️ Installation (méthode développeur)
```
## ⚠️ Pour les utilisateurs avancés uniquement
```bash
git clone https://github.com/Klyx-alm/Scan-bot.git
cd Scan-bot

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python bot/app.py
## 🧠 Problème courant (Port 5000 déjà utilisé)

Si l’application ne démarre pas :

Vérifier le port
lsof -i :5000
Tuer le processus
kill -9 PID

(Remplacer PID par le numéro affiché)
```
## 🌐 Accès

Une fois lancé, ouvrir dans le navigateur :

http://127.0.0.1:5000
## ⚠️ Disclaimer

Ce projet est destiné uniquement à des fins éducatives et de tests en cybersécurité (ethical hacking).

## ❗ N’utilisez cet outil que sur des systèmes pour lesquels vous avez une autorisation explicite.

## 👨‍💻 Auteur

ScanBot développé par Kelly ALONOMBA
