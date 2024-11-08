from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from config import Config

def create_driver():
  chrome_options = Options()
  for option in Config.CHROME_OPTIONS:
    chrome_options.add_argument(option)
    
  driver = webdriver.Chrome(options=chrome_options)
  return driver 