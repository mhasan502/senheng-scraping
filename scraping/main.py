from concurrent.futures import ThreadPoolExecutor

from bs4 import BeautifulSoup
import selenium.common.exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from unidecode import unidecode

from DataSaver import DataSaver
from WebDriver import WebDriverSingleton


def parse_product_list(category_: str) -> list:
    driver.get(f'https://www.senheng.com.my/all-products/{category_}.html')
    WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'jss113')))
    last_height = driver.execute_script('return document.body.scrollHeight')

    # while True:
    #     driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
    #     try:
    #         WebDriverWait(driver, 3).until(
    #             lambda x: x.execute_script(f'return document.body.scrollHeight > {last_height}')
    #         )
    #
    #         last_height = driver.execute_script('return document.body.scrollHeight')
    #     except selenium.common.exceptions.TimeoutException:
    #         break

    driver.execute_script('window.scrollTo(0, 0);')
    return driver.find_elements(By.CLASS_NAME, 'jss127')


def collect_product_information(page_source: str) -> None:
    soup = BeautifulSoup(page_source, 'html.parser')

    product_info = soup.find(class_='product__detail')
    product_name = product_info.find('h1').text

    product_discount = True if product_info.find(class_='discount-price') else False

    product_discount_price = unidecode(product_info.find(class_='discount-price').text.split(' ')[-1]) \
        if product_discount \
        else None

    product_price = unidecode(product_info.find(class_='simple_product_price').text) \
        if product_discount \
        else unidecode(product_info.find('span', attrs={'class': 'price_text'}).text) \
        if product_info.find('span', attrs={'class': 'price_text'}) is not None \
        else None

    product_price = product_price.split(' ')[-1] if product_price is not None else None

    voucher_amount = int(product_info.find('span', attrs={'style': 'font-weight: bold;'}).text.split(' ')[0][2:])

    availability = True \
        if soup.find_all('span', attrs={'class': 'MuiButton-label'})[-1].text != 'OUT OF STOCK' \
        else False

    data_saver.add_data(
        data={
            'product_name': product_name,
            'product_price': product_price,
            'product_discount_price': product_discount_price,
            'voucher_amount': voucher_amount,
            'availability': availability
        }
    )


if __name__ == '__main__':
    driver = WebDriverSingleton()
    data_saver = DataSaver()
    malformed_link = 0

    category_list = ['mobiles-tablets', 'digital-gadgets', 'computers-laptops']

    for category in category_list:
        product_list_of_links = parse_product_list(category_=category)

        length_of_product_list = len(product_list_of_links)
        print(f'Total number of products: {length_of_product_list}')

        for i in range(length_of_product_list):
            product_list_of_links[i].click()
            try:
                WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CLASS_NAME, 'product__detail')))
                with ThreadPoolExecutor(max_workers=8) as executor:
                    executor.submit(collect_product_information, driver.page_source)
            except selenium.common.exceptions.TimeoutException:  # throws when product not found due to 404
                malformed_link += 1
                continue
            finally:
                product_list_of_links = parse_product_list(category_=category)

        data_saver.save_data(file_name=category)
        print(f"Number of malformed link in {category} is: {malformed_link}")
        malformed_link = 0

    driver.quit()
