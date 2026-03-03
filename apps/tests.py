from seleniumwire import webdriver  # selenium o'rniga seleniumwire ishlatiladi
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

options = webdriver.ChromeOptions()
options.add_argument('--headless')

# Drayverni ishga tushirish
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://uzum.uz/uz/category/mebel-2894"

try:
    print("Sahifa yuklanmoqda...")
    driver.get(url)
    time.sleep(10)  # API so'rovlari almashishi uchun vaqt beramiz

    json_found = False
    for request in driver.requests:
        if request.response:
            # Uzum ma'lumotlarni asosan 'graphql' yoki 'category' so'rovlari orqali oladi
            if 'operationName=getCategory' in request.url or 'search' in request.url:
                body = request.response.body

                # Ma'lumotni dekodlash
                data = json.loads(body.decode('utf-8'))

                # JSON faylga saqlash
                with open('uzum_api_data.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)

                print("Haqiqiy JSON ma'lumotlari 'uzum_api_data.json' fayliga saqlandi!")
                json_found = True
                break

    if not json_found:
        print("JSON so'rovi topilmadi. Sahifani qayta yuklab ko'ring.")

finally:
    driver.quit()