import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()

driver.get("https://www.youtube.com/watch?v=DORZA_S7f9w")
# driver.get("https://youtu.be/b6wAYwOKgRY")

time.sleep(5)

# element = WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#details')))
titles = driver.find_element(By.CSS_SELECTOR, "#above-the-fold #title .ytd-watch-metadata .style-scope")
print(titles.text)