


#!/usr/bin/env python3 
import os 
import time 
import json 
import random 
from dotenv import load_dotenv 
from selenium import webdriver 
from selenium.webdriver.common.by import By 
from selenium.webdriver.chrome.options import Options 
from selenium.common.exceptions import TimeoutException, NoSuchElementException 
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC 
from webdriver_manager.chrome import ChromeDriverManager

load_dotenv()

CONFIG_PATH = os.environ.get("DICEBOT_CONFIG", "config.json") BETFURY_URL = os.environ.get("BETFURY_URL", "https://betfury.io") EMAIL = os.environ.get("BETFURY_EMAIL", "") PASSWORD = os.environ.get("BETFURY_PASSWORD", "") HEADLESS = os.environ.get("HEADLESS", "true").lower() in ("1", "true", "yes") ROUNDS = int(os.environ.get("ROUNDS", "10")) DELAY = float(os.environ.get("DELAY", "2.0"))

def load_config(path): with open(path, "r", encoding="utf-8") as f: return json.load(f)

def start_driver(headless=True): chrome_options = Options() if headless: # use the newer headless mode if available chrome_options.add_argument("--headless=new") chrome_options.add_argument("--disable-gpu") chrome_options.add_argument("--no-sandbox") chrome_options.add_argument("--window-size=1600,900") driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options) return driver

def safe_find(driver, by, selector, timeout=8): try: return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, selector))) except TimeoutException: return None

def click_if_present(driver, by, selector, timeout=6): el = safe_find(driver, by, selector, timeout) if el: try: el.click() return True except Exception: return False return False

def send_keys_if_present(driver, by, selector, text, timeout=6): el = safe_find(driver, by, selector, timeout) if el: el.clear() el.send_keys(text) return True return False

def wait_for_login(driver, cfg): # Two strategies: a 'login_check_selector' presence OR manual wait until user confirms sel = cfg.get("login_check_selector") timeout = cfg.get("login_check_timeout", 60) if sel: by = getattr(By, cfg.get("login_check_by", "CSS").upper(), By.CSS_SELECTOR) try: WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, sel))) print("Login detected (login_check_selector found).") return True except TimeoutException: print("Timeout waiting for login_check_selector.") return False else: input("Please complete login manually in the opened browser, then press Enter here to continue...") return True

def parse_result_text(driver, cfg): sel = cfg.get("result_selector") if not sel: return None by = getattr(By, cfg.get("result_by", "CSS").upper(), By.CSS_SELECTOR) el = safe_find(driver, by, sel, timeout=10) if not el: return None text = el.text.strip().lower() return text

def run_bot(): cfg = load_config(CONFIG_PATH) driver = start_driver(HEADLESS) driver.get(BETFURY_URL) print(f"Opened {BETFURY_URL}")
# optional: click initial login button to open login modal
lb_sel = cfg.get("login_button_selector")
if lb_sel:
    by = getattr(By, cfg.get("login_button_by", "CSS").upper(), By.CSS_SELECTOR)
    if click_if_present(driver, by, lb_sel):
        print("Clicked login button (if present).")
        time.sleep(1)

# If email/password selectors defined, attempt automated login
email_sel = cfg.get("email_selector")
pass_sel = cfg.get("password_selector")
submit_sel = cfg.get("login_submit_selector")

if EMAIL and PASSWORD and email_sel and pass_sel:
    print("Trying automated email/password login...")
    by_email = getattr(By, cfg.get("email_by", "CSS").upper(), By.CSS_SELECTOR)
    by_pass = getattr(By, cfg.get("password_by", "CSS").upper(), By.CSS_SELECTOR)
    send_ok = send_keys_if_present(driver, by_email, email_sel, EMAIL)
    send_ok &= send_keys_if_present(driver, by_pass, pass_sel, PASSWORD)
    if send_ok and submit_sel:
        by_submit = getattr(By, cfg.get("login_submit_by", "CSS").upper(), By.CSS_SELECTOR)
        click_if_present(driver, by_submit, submit_sel)
        print("Submitted login form.")
    else:
        print("Could not find login form elements; may require manual login.")
else:
    print("Automated credentials not provided or selectors missing. Will wait for manual login if needed.")

# Wait until logged in (using config or manual)
if not wait_for_login(driver, cfg):
    print("Login failed or timed out — exiting.")
    driver.quit()
    return

# After logged in: play dice loop
bet_sel = cfg.get("bet_amount_selector")
roll_sel = cfg.get("roll_button_selector")
balance_sel = cfg.get("balance_selector")
bet_by = getattr(By, cfg.get("bet_amount_by", "CSS").upper(), By.CSS_SELECTOR)
roll_by = getattr(By, cfg.get("roll_button_by", "CSS").upper(), By.CSS_SELECTOR)
balance_by = getattr(By, cfg.get("balance_by", "CSS").upper(), By.CSS_SELECTOR)

if not roll_sel:
    print("No roll_button_selector configured — cannot perform automated rolls. Exiting.")
    driver.quit()
    return

rounds = ROUNDS
print(f"Starting betting loop for {rounds} rounds (delay {DELAY}s).")
wins = 0
losses = 0

for i in range(rounds):
    try:
        # choose bet amount (can be fixed or random)
        amount = cfg.get("bet_amount_fixed")
        if amount is None:
            # random between min and max in config
            min_b = cfg.get("bet_amount_min", 0.0001)
            max_b = cfg.get("bet_amount_max", 0.001)
            amount = round(random.uniform(min_b, max_b), 8)

        if bet_sel:
            el_bet = safe_find(driver, bet_by, bet_sel, timeout=6)
            if el_bet:
                try:
                    el_bet.clear()
                    el_bet.send_keys(str(amount))
                except Exception:
                    pass

        click_if_present(driver, roll_by, roll_sel)
        print(f"[{i+1}/{rounds}] Rolled with amount {amount}...")

        # wait for result to appear
        time.sleep(DELAY)
        res_text = parse_result_text(driver, cfg)
        if res_text:
            # naive determination: if contains 'win' / 'lose' keywords
            if "win" in res_text or "выиграл" in res_text or "won" in res_text:
                wins += 1
                print(f"Result: WIN ({res_text})")
            else:
                losses += 1
                print(f"Result: LOSS ({res_text})")
        else:
            print("Result text not found; skipping result parse.")

        # optionally get balance
        if balance_sel:
            try:
                bal_el = safe_find(driver, balance_by, balance_sel, timeout=3)
                if bal_el:
                    print("Balance:", bal_el.text.strip())
            except Exception:
                pass

        # small random delay
        time.sleep(cfg.get("between_rounds_delay", 1.0))
    except Exception as e:
        print("Exception during betting loop:", e)

print("Session finished. Wins:", wins, "Losses:", losses)
driver.quit()


if name == "main": run_bot()
