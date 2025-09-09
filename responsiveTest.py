import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from applitools.selenium import Eyes, Target, BatchInfo
from applitools.common import DeviceName, ScreenOrientation

# -----------------------------
# Applitools API Key
# -----------------------------
APPLITOOLS_API_KEY = os.environ.get("APPLITOOLS_API_KEY", "YOUR_API_KEY")
batch = BatchInfo("BThere - Local Selenium Custom Baselines")

# -----------------------------
# Pages to Test
# -----------------------------
PAGES = [
    {"name": "Home Page", "url": "https://b-there.in/"},
    {"name": "QR Generator Page", "url": "https://b-there.in/sf/qr-generator"},
    # {"name": "Product Page", "url": "https://bthere.com/product"},
]

# -----------------------------
# Viewports / Devices
# -----------------------------
VIEWPORTS = [
    {"name": "Desktop - 1920x1080", "width": 1920, "height": 1080},
    {"name": "Laptop - 1366x768", "width": 1366, "height": 768},
    {"name": "iPad Mini Portrait", "device": DeviceName.iPad_Mini, "orientation": ScreenOrientation.PORTRAIT},
    {"name": "iPad Mini Landscape", "device": DeviceName.iPad_Mini, "orientation": ScreenOrientation.LANDSCAPE},
    {"name": "iPhone_14_Plus Portrait", "device": DeviceName.iPhone_14_Plus, "orientation": ScreenOrientation.PORTRAIT},
    {"name": "iPhone_14_Plus Landscape", "device": DeviceName.iPhone_14_Plus, "orientation": ScreenOrientation.LANDSCAPE},
]

# -----------------------------
# Chrome Options
# -----------------------------
def get_chrome_options():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    return chrome_options

# -----------------------------
# Run Visual Tests
# -----------------------------
def run_visual_test():
    eyes = Eyes()
    eyes.api_key = APPLITOOLS_API_KEY
    eyes.batch = batch

    for config in VIEWPORTS:
        for page in PAGES:
            driver = None
            try:
                chrome_options = get_chrome_options()

                # Device emulation
                if "device" in config:
                    mobile_emulation = {"deviceName": config["device"].value}
                    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

                # Start Chrome directly
                driver = webdriver.Chrome(options=chrome_options)

                # Window resize for desktop/laptop
                if "width" in config:
                    driver.set_window_size(config["width"], config["height"])

                eyes.open(driver, "BThere App", f"{page['name']} - {config['name']}")
                print(f"🌍 Opening {page['url']} on {config['name']}...")

                driver.get(page["url"])

                # Wait until page body is loaded
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                time.sleep(3)  # give extra render time

                eyes.check(page["name"], Target.window().fully())
                eyes.close(False)
                print(f"✅ Captured {page['name']} on {config['name']}")

            except Exception as e:
                print(f"❌ Error on {page['name']} for {config['name']}: {e}")
                eyes.abort_async()
            finally:
                if driver:
                    driver.quit()

if __name__ == "__main__":
    run_visual_test()
    print("✅ All visual tests completed. Check Applitools dashboard.")
