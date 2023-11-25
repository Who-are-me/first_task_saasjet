import time
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.implicitly_wait(5)
driver.get("https://www.youtube.com/watch?v=N8siuNjyV7A")
# time.sleep(5)
link_element = driver.find_element(By.XPATH, '//*[@id="title"]/h1/yt-formatted-string')
# time.sleep(2)
print(link_element.text)
# print(driver.title)
