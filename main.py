import csv
import re
import time
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


def scrape_reviews(url, n, filename, driver):
    print("Membuka browser!!!")
    driver.maximize_window()
    actions = ActionChains(driver)
    results = list()
    print("Memulai scraping!!!!")

    old_url = url
    for i in range(n):
        driver.get(old_url)
        print(f"Halaman: {i+1}")
        finish_time = time.time() + 10

        #scroll page supaya semua elemen dimuat
        while time.time() < finish_time:
            actions.send_keys(Keys.PAGE_DOWN)
            actions.perform()
            time.sleep(1)

        #parsing ke beautifulsoup
        souped = BeautifulSoup(driver.page_source, "html.parser")
        containers = souped.select('div[data-test-target="HR_CC_CARD"]')

        for container in containers:
            #tanggal review
            month_pattern = r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Yesterday|yesterday)\s?(\d{,4})?"
            date_tag = container.select_one("div.bcaHz span")
            date_txt = date_tag.get_text(strip=True, separator=" ")
            date_pattern = re.compile(month_pattern)
            month_year = date_pattern.search(date_txt)
            year = month_year.group(2)
            month = month_year.group(1)
            if year is None or year != "2021":
                #mengubah yesterday menjadi bulan
                if month.lower() == "yesterday":
                    date_today = datetime.now()
                    month = date_today.strftime("%b")

                #mengubah hari menjadi tahun
                if year is None or len(year) < 4:
                    year = "2022"

                date_review = datetime.strptime(month + " " + year, "%b %Y")

                #isi review
                content_tag = container.select_one("q.XllAv.H4._a")
                content_txt = content_tag.get_text(strip=True)

                #untuk membersihkan teks dari emoji atau karakter yg tidak perlu
                ascii_pattern = re.compile(r"[\x21-\x7E\x80-\xFF]+")
                content_clear = ascii_pattern.findall(content_txt)
                content_review = " ".join(content_clear)

                #rating review
                rating_tag = container.select_one("div[data-test-target='review-rating'] span")
                rating_attr = rating_tag["class"]
                rating_text = rating_attr[1].split("_")
                rating_review = ".".join(list(rating_text[1]))

                hotel_reviews = {
                        "Date": date_review.strftime("%B %Y"),
                        "Rating": float(rating_review),
                        "Content": content_review
                }

                print("Berhasil...")
                results.append(hotel_reviews)

        time.sleep(1)

        #menekan tombol next untuk ke halaman selanjutnya
        next_page_tag = souped.select_one("a.ui_button.nav.next.primary")
        next_page_link = urljoin("https://www.tripadvisor.com", next_page_tag["href"])
        old_url = next_page_link

    print(f"Hasil = {len(results)}")

    #menutup browser
    driver.quit()

    print("Menyimpan ke file csv!!!!")
    # menyimpan ke file csv
    file = open(filename, "w", newline="")
    csvwriter = csv.DictWriter(file, fieldnames=("Date", "Rating", "Content"), delimiter=";")
    csvwriter.writeheader()
    for result in results:
        csvwriter.writerow(result)
    file.close()
    print("Berhasil...")


# mengatur mode webdriver
options = Options()
# options.add_argument('--disable-extension')
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.page_load_strategy = 'eager'
options.add_experimental_option("detach", True)
browser = webdriver.Chrome(executable_path="chromedriver.exe", options=options)

#Hotel sterling mussoorie
scrape_reviews(
        url="https://www.tripadvisor.com/Hotel_Review-g297689-d1149675-Reviews-Sterling_Mussoorie-Mussoorie_Dehradun_District_Uttarakhand.html",
        n=12,
        filename="hotel_sterling_mussoorie.csv",
        driver=browser
)

#Hotel Ramada
# scrape_reviews(
#     url="https://www.tripadvisor.com/Hotel_Review-g297689-d627080-Reviews-Ramada_by_Wyndham_Mussoorie_Mall_Road-Mussoorie_Dehradun_District_Uttarakhand.html",
#     n=20,
#     filename="hotel_ramada.csv",
#     driver=browser
# )