class Config:
  DEBUG = True
  
  CHROME_OPTIONS = [
    "--headless",
    "--no-sandbox",
    "--disable-dev-shm-usage"
  ] 