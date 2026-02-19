import os
import requests
import re
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Setup browser
options = Options()
options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=options)

driver.get("https://elpais.com/opinion/")

translated_titles = []

# Wait for articles
articles = WebDriverWait(driver, 15).until(
    EC.presence_of_all_elements_located((By.TAG_NAME, "article"))
)

print("Processing first 5 articles...\n")

article_links = []

for article in articles:
    try:
        link = article.find_element(By.CSS_SELECTOR, "h2 a").get_attribute("href")
        if link and link.startswith("https"):
            article_links.append(link)
    except:
        continue

article_links = article_links[:5]

# Translation function
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

for link in article_links:
    driver.get(link)

    try:
        title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        ).text.strip()

        print("Spanish Title:", title)

        english_title = translate_text(title)
        translated_titles.append(english_title)

        print("English Title:", english_title)

    except:
        print("Failed to extract title")
        continue

    # Simple content extraction
    paragraphs = driver.find_elements(By.TAG_NAME, "p")
    content = "\n".join([p.text for p in paragraphs if len(p.text.strip()) > 50])

    print("Content preview:", content[:300], "...\n")

# Word frequency analysis
print("\nAll Translated Titles:")
for t in translated_titles:
    print(t)

combined_text = " ".join(translated_titles).lower()
clean_text = re.sub(r"[^\w\s]", "", combined_text)

words = clean_text.split()
stopwords = {"the", "and", "of", "in", "to", "a", "for", "on", "with", "is", "that"}

filtered_words = [w for w in words if w not in stopwords]
word_count = Counter(filtered_words)

print("\nWords repeated more than twice:")
for word, count in word_count.items():
    if count > 2:
        print(f"{word} → {count} times")

driver.quit()