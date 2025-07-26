import pandas as pd
import time
import os
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

# === Argument parser pour l'envoi d'image ===
parser = argparse.ArgumentParser()
parser.add_argument("--image", action="store_true", help="Envoyer une image avec le message")
args = parser.parse_args()

# === Chemins ===
CSV_FILE = "uploads/uploaded.csv"
MESSAGE_FILE = "message.txt"
IMAGE_FILE = "image.jpg"
HISTORIQUE_FILE = "historique_envoyes.csv"
DELAI_ENTRE_MESSAGES = 5
NB_MESSAGES_MAX = 50

# === Lecture des données ===
df = pd.read_csv(CSV_FILE)
df["numero"] = df["numero"].astype(str).str.replace(r"\D", "", regex=True)

with open(MESSAGE_FILE, "r", encoding="utf-8") as f:
    message_template = f.read()

# === Historique
if os.path.exists(HISTORIQUE_FILE):
    deja_envoyes = pd.read_csv(HISTORIQUE_FILE)
    deja_envoyes.columns = deja_envoyes.columns.str.strip()
    nums_envoyes = set(deja_envoyes["numero"].astype(str).str.replace(r"\D", "", regex=True))
else:
    nums_envoyes = set()

# === Lancer Chrome
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=Service(), options=options)
driver.get("https://web.whatsapp.com/")
print("📲 Scanne le QR Code si besoin...")
time.sleep(10)

# ✅ Fermer popup s’il existe
try:
    close_popup = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(),'Continuer')]]"))
    )
    close_popup.click()
    print("✅ Popup WhatsApp fermé automatiquement.")
except:
    print("ℹ️ Aucun popup détecté.")

# === Envoi des messages
messages_envoyes = []

for index, row in df.iterrows():
    nom = row.get("nom", "")
    tel = str(row["numero"])

    if tel in nums_envoyes:
        print(f"⏭ Déjà envoyé : {nom} ({tel})")
        continue

    if not tel.startswith("336") and not tel.startswith("337"):
        print(f"❌ Numéro non mobile ignoré : {tel}")
        continue

    try:
        message = message_template.replace("{{nom}}", nom)
        url = f"https://web.whatsapp.com/send?phone={tel}"
        driver.get(url)
        print(f"📨 Conversation avec {nom} ({tel})...")
        time.sleep(5)

        message_box = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']"))
        )
        message_box.click()
        message_box.send_keys(message)
        time.sleep(1)
        message_box.send_keys(Keys.ENTER)

        # === Image
        if args.image and os.path.exists(IMAGE_FILE):
            attach_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-icon='clip']"))
            )
            attach_btn.click()

            img_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
            )
            img_input.send_keys(os.path.abspath(IMAGE_FILE))
            time.sleep(2)

            send_img_btn = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span[data-icon='send']"))
            )
            send_img_btn.click()

        print(f"✅ Message envoyé à {nom} ({tel})")
        messages_envoyes.append({"nom": nom, "numero": tel})
        nums_envoyes.add(tel)
        time.sleep(DELAI_ENTRE_MESSAGES)

        if len(messages_envoyes) >= NB_MESSAGES_MAX:
            print(f"⏹ Limite de {NB_MESSAGES_MAX} messages atteinte.")
            break

    except Exception as e:
        print(f"❌ Échec pour {nom} ({tel}) : {e}")

# === Historique
if messages_envoyes:
    df_envoyes = pd.DataFrame(messages_envoyes)
    if os.path.exists(HISTORIQUE_FILE):
        df_existing = pd.read_csv(HISTORIQUE_FILE)
        df_existing.columns = df_existing.columns.str.strip()
        df_combined = pd.concat([df_existing, df_envoyes]).drop_duplicates(subset="numero")
    else:
        df_combined = df_envoyes

    df_combined.to_csv(HISTORIQUE_FILE, index=False)
    print(f"💾 Historique mis à jour avec {len(messages_envoyes)} contacts.")

driver.quit()
