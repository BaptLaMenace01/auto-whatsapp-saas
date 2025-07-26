import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

def launch_campaign(campaign_id, contacts, message_template, options):
    delay = int(options.get("delay_between_messages", 1000)) / 1000
    include_image = options.get("include_image", False)

    driver = webdriver.Chrome(service=Service())
    driver.get("https://web.whatsapp.com/")
    print("📲 Scanne le QR Code...")
    time.sleep(15)

    results = {
        "total": len(contacts),
        "sent": 0,
        "failed": 0,
        "details": []
    }

    for contact in contacts:
        name = contact.get("name", "")
        phone = contact.get("phone", "").replace("+", "").replace(" ", "")
        message = message_template.replace("{{name}}", name)

        try:
            url = f"https://web.whatsapp.com/send?phone={phone}"
            driver.get(url)
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']"))
            )
            box = driver.find_element(By.CSS_SELECTOR, "div[contenteditable='true'][data-tab='10']")
            box.click()
            box.send_keys(message)
            box.send_keys(Keys.ENTER)

            results["sent"] += 1
            results["details"].append({
                "phone": phone,
                "status": "sent",
                "timestamp": datetime.utcnow().isoformat()
            })

        except Exception as e:
            results["failed"] += 1
            results["details"].append({
                "phone": phone,
                "status": "failed",
                "error": str(e)
            })

        time.sleep(delay)

    driver.quit()
    return results
