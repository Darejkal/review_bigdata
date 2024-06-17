from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import json
import time
import re
import requests
import glob
import os



def get_comment_and_rating(driver):
    blocks = driver.find_elements(By.XPATH, "//div[contains(@class, 'style__StyledComment-sc-1y8vww-5 dpVjwc review-comment')]")
    sample_list = []
    for sample in blocks:
        # Find the child div with the class name 'review-comment__title' within each comment
        try:
            rate = sample.find_element(By.XPATH, ".//div[contains(@class, 'review-comment__title')]")
            review = sample.find_element(By.XPATH, ".//div[contains(@class, 'review-comment__content')]")
            comment = ""
            try:
                show_more = review.find_element(By.XPATH, ".//span[contains(@class, 'show-more-content')]")
                show_more.click()
                time.sleep(1)
                comment = review.find_element(By.XPATH, './/span[1]').text
            except:
                comment = review.text

            # Get the text of the child div
            if len(comment.split()) > 3: 
                print(f"{comment} - {rate.text}")
                print('-------------------------------------------------')
                sample = dict()
                sample["comment"] = comment
                sample["rate"] = rate.text
                sample_list.append(sample)
        except:
            continue
    return sample_list

def get_comment_and_rating_url(url, driver):
    try:
        # Navigate to the desired webpage
        driver.get(url)

        # Allow some time for the page to load
        time.sleep(10)

        # Scroll down slowly
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            # Scroll down by a small amount
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(10)

            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        next_button = ""
        samples = []
        while next_button is not None:
            try:
                next_button = driver.find_element(By.XPATH, "//a[contains(@class, 'btn next')]")
                next_button.click()
                time.sleep(1)
            except:
                next_button = None
            samples.extend(get_comment_and_rating(driver))
        return samples

    finally:
        # Close the WebDriver
        driver.quit()

if __name__ == "__main__":
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3', 
    'Accept': 'application/json',
    # 'Authorization': 'Bearer YOUR_ACCESS_TOKEN'  # Uncomment and set if authorization is required
    }
    txt_files = glob.glob('data/*.txt')
    for file in txt_files:
        filename = file.split('/')[1][:-4]
        print(filename)
        with open(file, 'r') as f:
            lines = f.readlines()
        review_list = []

        for id, line in enumerate(lines):
            line = 'https://tiki.vn' + line
            print(line)
            pattern = r"p(\d+)"
            match = re.search(pattern, line)
            number = match.group(1)
            page = 1
            while True:
                url = f"https://tiki.vn/api/v2/reviews?product_id={number}&page={page}"
                try:
                    response = requests.get(url, headers=headers)
                    response = response.json()
                    if len(response["data"]) == 0:
                        break
                    for review in response["data"]:
                        print(review)
                        review_list.append(review)
                    page += 1
                except:
                    break
        with open(f"data/json/{filename}.json", 'w', encoding='utf-8') as fout:
            json.dump(review_list , fout)     


# data = get_comment_and_rating_url("https://tiki.vn/ikigai-bi-mat-song-truong-tho-va-hanh-phuc-cua-nguoi-nhat-p10095276.html?spid=10095277", driver)

# with open('test.json', 'w', encoding='utf-8') as fout:
#     json.dump(data , fout)

