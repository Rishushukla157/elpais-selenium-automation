import requests
import re
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import threading

USERNAME = "your_browserstack_username"
ACCESS_KEY = "your_browserstack_access_key"

BROWSERSTACK_URL = f"https://{USERNAME}:{ACCESS_KEY}@hub-cloud.browserstack.com/wd/hub"


def translate_text(text):
    url = "https://translate.googleapis.com/translate_a/single"
    params = {
        "client": "gtx",
        "sl": "es",
        "tl": "en",
        "dt": "t",
        "q": text
    }
    response = requests.get(url, params=params)
    return response.json()[0][0][0]


def run_test(bstack_options):
    options = webdriver.ChromeOptions()
    options.set_capability("bstack:options", bstack_options)
    options.set_capability("browserName", bstack_options["browserName"])
    options.set_capability("browserVersion", "latest")

    driver = webdriver.Remote(
        command_executor=BROWSERSTACK_URL,
        options=options
    )

    translated_titles = []

    try:
        driver.get("https://elpais.com/opinion/")

        articles = WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "article"))
        )

        article_links = []

        for article in articles:
            try:
                link = article.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
                if link and link.startswith("https"):
                    article_links.append(link)
            except:
                continue

        article_links = article_links[:5]

        for link in article_links:
            driver.get(link)

            try:
                title = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "h1"))
                ).text.strip()

                english_title = translate_text(title)
                translated_titles.append(english_title)

            except:
                continue

        combined_text = " ".join(translated_titles).lower()
        clean_text = re.sub(r"[^\w\s]", "", combined_text)
        words = clean_text.split()

        stopwords = {"the", "and", "of", "in", "to", "a", "for", "on", "with", "is", "that"}
        filtered_words = [w for w in words if w not in stopwords]

        word_count = Counter(filtered_words)

        print("\nRepeated words (>2 times):")
        for word, count in word_count.items():
            if count > 2:
                print(f"{word} → {count}")

    finally:
        driver.quit()


# 5 browser configurations
configs = [
    {
        "browserName": "Chrome",
        "os": "Windows",
        "osVersion": "11",
        "buildName": "ElPais Parallel Build",
        "sessionName": "Windows Chrome"
    },
    {
        "browserName": "Firefox",
        "os": "Windows",
        "osVersion": "10",
        "buildName": "ElPais Parallel Build",
        "sessionName": "Windows Firefox"
    },
    {
        "browserName": "Safari",
        "os": "OS X",
        "osVersion": "Ventura",
        "buildName": "ElPais Parallel Build",
        "sessionName": "Mac Safari"
    },
    {
        "browserName": "Chrome",
        "os": "Android",
        "osVersion": "13.0",
        "deviceName": "Samsung Galaxy S23",
        "realMobile": "true",
        "buildName": "ElPais Parallel Build",
        "sessionName": "Android Test"
    },
    {
        "browserName": "Safari",
        "os": "iOS",
        "osVersion": "16",
        "deviceName": "iPhone 14",
        "realMobile": "true",
        "buildName": "ElPais Parallel Build",
        "sessionName": "iOS Test"
    }
]

threads = []

for config in configs:
    thread = threading.Thread(target=run_test, args=(config,))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

print("Parallel execution complete.")
