# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
import time
import requests

# Setup Chrome options
# chrome_options = Options()
# # chrome_options.add_argument("--headless")  # Ensure GUI is off
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")

# # Set up the WebDriver using WebDriverManager
# service = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=service, options=chrome_options)

def crawl_all_urls(url):
    try:
        driver.get(url)  # Update with the correct URL

    # Allow some time for the page to load
        time.sleep(5)
        # Find button
        topics = driver.find_elements(By.XPATH, "//div[contains(@class, 'styles__TreeItemStyled-sc-1uq9a9i-2 ThXqv')]")
        total_url = []
        for topic in topics:
            href = topic.find_element(By.XPATH, "./a").get_attribute('href')
            total_url.append(href)
        topics = driver.find_elements(By.XPATH, "//div[contains(@class, 'styles__TreeSubItem-sc-1uq9a9i-6 divFYE')]")
        for topic in topics:
            href = topic.find_element(By.XPATH, "./a").get_attribute('href')
            total_url.append(href)
        
        buttons = driver.find_elements(By.XPATH, "//div[contains(@class, 'styles__TreeIcon-sc-1uq9a9i-4 kJopVc')]")
        for button in buttons[1:]:
            button.click()
            time.sleep(1)
            topics = driver.find_elements(By.XPATH, "//div[contains(@class, 'styles__TreeSubItem-sc-1uq9a9i-6 divFYE')]")
            for topic in topics:
                href = topic.find_element(By.XPATH, "./a").get_attribute('href')
                total_url.append(href)
        all_url = [u for u in total_url]
        for link in total_url:
            all_url.extend(crawl_all_urls(link))
        return all_url
    except:
        return []

list_urls = [
    "/nha-cua-doi-song/c1883",
    "/dien-thoai-may-tinh-bang/c1789",
    "/do-choi-me-be/c2549",
    "/thiet-bi-kts-phu-kien-so/c1815",
    "/dien-gia-dung/c1882",
    "/lam-dep-suc-khoe/c1520",
    "/o-to-xe-may-xe-dap/c8594",
    "/thoi-trang-nu/c931",
    "/bach-hoa-online/c4384",
    "/the-thao-da-ngoai/c1975",
    "/thoi-trang-nam/c915",
    "/cross-border-hang-quoc-te/c17166",
    "/laptop-may-vi-tinh-linh-kien/c1846",
    "/giay-dep-nam/c1686",
    "/dien-tu-dien-lanh/c4221",
    "/giay-dep-nu/c1703",
    "/may-anh/c1801",
    "/phu-kien-thoi-trang/c27498",
    "/ngon/c44792",
    "/dong-ho-va-trang-suc/c8371",
    "/balo-va-vali/c6000"
    "/voucher-dich-vu/c11312",
    "/tui-vi-nu/c976",
    "/tui-thoi-trang-nam/c27616",
    "/cham-soc-nha-cua/c15078"
]


try:
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3', 
    'Accept': 'application/json',
    # 'Authorization': 'Bearer YOUR_ACCESS_TOKEN'  # Uncomment and set if authorization is required
    }
    with open('all_url.txt', 'r') as f:
        urls = f.readlines()
        for url in urls:
            url_product_list = []
            print(f"BLABLA {url}")
            li = url.split('/')
            categories, id = li[-2], li[-1][1:]
            categories = categories.strip('\n').strip()
            id = int(id)
            page = 1
            while True:
                link = f"https://tiki.vn/api/personalish/v1/blocks/listings?limit=40&include=advertisement&aggregations=2&version=home-persionalized&category={id}&page={page}&urlKey={categories}"
                print(link)
                try:
                    response = requests.get(link, headers=headers)
                    response = response.json()
                    if len(response["data"]) == 0:
                        break
                    for product in response["data"]:
                        url_product_list.append(product['url_path'])
                        print(product['url_path'])
                    page += 1
                except:
                    break
            with open(f"data/{categories}.txt", 'w') as f:
                for p in url_product_list:
                    f.writelines(p + '\n')
finally:
    # Close the WebDriver
    driver.quit()
