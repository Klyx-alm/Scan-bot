# 🚀 ScanBot (Version Mac dispo pour le moment)

ScanBot est un outil de cybersécurité permettant d'analyser des machines via leur adresse IP avec une interface web moderne et un assistant IA intégré.

## 🔥 Fonctionnalités
- Scan rapide
- Deep scan
- Détection OS
- Analyse intelligente
- Gobuster directory brute-force
- Chat AI intégré

⚠️ Important:
OS detection requires administrator privileges.

Mac/Linux:
sudo ./ScanBot

Windows:
Run Scanbot as Administrator in terminal

## Téléchargement
Aller sur le https://github.com/Klyx-alm/Scan-bot/releases 
puis télécharger le fichier ScanBot.zip 
Décompresser le puis cliquer sur l'app sans passer à la phase installation en bas

## ⚙️ Installation (Autres méthodes)

```bash
git clone https://github.com/Klyx-alm/Scan-bot/archive/refs/tags/v1.0.zip
cd scanbot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python bot/app.py

## Après la première utilisation le localhost est deja utiliser donc faire :
lsof -i :5000 ## Pour voir si le port 5000 est vraiment utiliser 

## Si oui après faire :
kill -9 PID ## Pour couper l'utilisation du port (Remplacer PID par le vrai numéro)

🌐 Accès

Une fois lancé, ouvre ton navigateur :

http://127.0.0.1:5000

⚠️ Disclaimer

Ce projet est destiné uniquement à des fins éducatives et de tests en cybersécurité (ethical hacking).
N'utilisez cet outil que sur des systèmes dont vous avez l'autorisation.

👨‍💻 Auteur

ScanBot développé par Kelly ALONOMBA
