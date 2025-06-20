from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from textblob import TextBlob

# Set ChromeDriver Path
CHROMEDRIVER_PATH = "C:\\Windows\\chromedriver.exe"

def scrape_comments(instagram_url):
    options = Options()
    options.headless = True  # Run in headless mode (no visible browser)
    options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(CHROMEDRIVER_PATH)

    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(instagram_url)
        time.sleep(5)  # Wait for comments to load

        comments = []
        comment_elements = driver.find_elements(By.CSS_SELECTOR, "ul li div div div span")

        for elem in comment_elements:
            comment_text = elem.text.strip()
            if comment_text:
                comments.append(comment_text)

        driver.quit()

        return analyze_sentiments(comments)

    except Exception as e:
        driver.quit()
        return {"error": str(e)}

def analyze_sentiments(comments):
    results = {"positive": [], "negative": [], "neutral": []}

    for comment in comments:
        sentiment_score = TextBlob(comment).sentiment.polarity

        if sentiment_score > 0:
            results["positive"].append(comment)
        elif sentiment_score < 0:
            results["negative"].append(comment)
        else:
            results["neutral"].append(comment)

    return results
