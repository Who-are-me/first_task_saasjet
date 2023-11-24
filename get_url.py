import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# support global values
driver = webdriver.Chrome()
driver.implicitly_wait(5)
test_url_search_requests = [
    'Never Gonna Give You Up',
    'rick astley',
    'chainsaw man',
    'russian war ship'
]
test_url_youtube_search_div = 'div#contents ytd-item-section-renderer>div#contents a#thumbnail'


# TODO skip None urls
# TODO filter shorts on/off
# TODO skip lives, ad
# TODO add time limit
'''WARNING one request -> list, multi request -> map'''
def get_urls_of_youtube_request(list_of_search_requests: list = test_url_search_requests,
                                filter_pattern = test_url_youtube_search_div,
                                count: int = 10, silent=False):
    result = {}

    for request in list_of_search_requests:
        if silent:
            print("----DEBUG----")

        links = []
        driver.get(f'https://www.youtube.com/results?search_query={request}')
        link_webelements = driver.find_elements(By.CSS_SELECTOR, filter_pattern)

        while len(link_webelements) < count:
            driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
            time.sleep(1)
            # FIXME optimization
            link_webelements = driver.find_elements(By.CSS_SELECTOR, filter_pattern)

        if silent:
            print(link_webelements)
            print(f"Count link_webelements {len(link_webelements)}")

        for x in range(len(link_webelements)):
            if silent:
                print(x, end=" ")
                print(link_webelements[x].get_attribute('href'))

            links += [link_webelements[x-1].get_attribute('href')]

            if x == count-1:
                break


        if len(list_of_search_requests) == 1:
            return links

        result[request] = links

    if silent:
        print(result)

    return result


# TODO test & clean me
def get_urls_of_youtube_channel(channel_id = "wendoverproductions", show_title=False, count: int = 180):
    # links = []

    options = webdriver.ChromeOptions()
    # All are optional
    options.add_experimental_option("detach", True)
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-Advertisement")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("start-maximized")

    s = Service('./chromedriver')
    # driver = webdriver.Chrome(service=s, options=options)
    driver = webdriver.Chrome(options=options)

    driver.get(f'https://www.youtube.com/{channel_id}/videos')
    time.sleep(3)

    item = []
    SCROLL_PAUSE_TIME = 1
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    # item_count = 180

    while count > len(item):
        driver.execute_script("window.scrollTo(0,document.documentElement.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height

    data = []

    try:
        # TODO clean me pls
        for e in WebDriverWait(driver, 20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#details'))):
            title = e.find_element(By.CSS_SELECTOR, 'a#video-title-link').get_attribute('title')
            vurl = e.find_element(By.CSS_SELECTOR, 'a#video-title-link').get_attribute('href')
            # views = e.find_element(By.XPATH,
            #                        './/*[@id="metadata"]//span[@class="inline-metadata-item style-scope ytd-video-meta-block"][1]').text
            # date_time = e.find_element(By.XPATH,
            #                            './/*[@id="metadata"]//span[@class="inline-metadata-item style-scope ytd-video-meta-block"][2]').text
            if show_title:
                data.append({
                    title: vurl,
                    # 'title': title,
                    # 'date_time': date_time,
                    # 'views': views
                })
            else:
                data.append(vurl)
    except Exception as e:
        print(f"Error with {e}")

    return data

############################
# some code for testing file
############################

# print(get_urls_of_youtube_request(["cats"]))
# print(get_urls_of_youtube_channel("@AlekOS"))


