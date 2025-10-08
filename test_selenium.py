"""
Test script to verify Selenium setup
اختبار للتحقق من إعداد Selenium
"""
import sys

print("=" * 60)
print("Testing Selenium Setup / اختبار إعداد Selenium")
print("=" * 60)
print()

# Test 1: Check if Selenium is installed
print("1. Checking Selenium installation...")
try:
    import selenium
    print(f"   ✅ Selenium installed: version {selenium.__version__}")
except ImportError:
    print("   ❌ Selenium not installed!")
    print("   Run: pip install selenium==4.15.2")
    sys.exit(1)

# Test 2: Check webdriver-manager
print("\n2. Checking webdriver-manager installation...")
try:
    import webdriver_manager
    print(f"   ✅ webdriver-manager installed")
except ImportError:
    print("   ❌ webdriver-manager not installed!")
    print("   Run: pip install webdriver-manager==4.0.1")
    sys.exit(1)

# Test 3: Try to initialize Chrome WebDriver
print("\n3. Testing Chrome WebDriver initialization...")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    
    print("   Installing/updating ChromeDriver...")
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # Run without window
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    print(f"   ChromeDriver installed at: {service.path}")
    
    print("   Initializing Chrome...")
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("   Testing navigation...")
    driver.get("https://www.google.com")
    print(f"   Page title: {driver.title}")
    
    driver.quit()
    print("   ✅ Chrome WebDriver works perfectly!")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    print("\n   Possible solutions:")
    print("   1. Install Chrome browser: https://www.google.com/chrome/")
    print("   2. Update selenium: pip install --upgrade selenium")
    print("   3. Clear webdriver cache: rm -rf ~/.wdm")
    sys.exit(1)

# Test 4: Test scraping capability
print("\n4. Testing scraping capability...")
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from webdriver_manager.chrome import ChromeDriverManager
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    print("   Navigating to LiftMaster website...")
    driver.get("https://www.liftmaster-me.com")
    print(f"   Page loaded: {driver.title}")
    
    # Try to find some links
    links = driver.find_elements(By.TAG_NAME, "a")
    print(f"   Found {len(links)} links on the page")
    
    driver.quit()
    print("   ✅ Scraping capability works!")
    
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! / جميع الاختبارات نجحت!")
print("=" * 60)
print("\nYou can now use the scraping feature in the admin panel.")
print("يمكنك الآن استخدام ميزة الجلب من لوحة التحكم.")
print()

