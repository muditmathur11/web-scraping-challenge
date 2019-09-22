# Import dependencies
from splinter import Browser
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt

# Create function
def scrape_all():

    #Set up path to splinter browser
    executable_path = {'executable_path': 'chromedriver.exe'}
    browser = Browser('chrome', **executable_path, headless=False)
    page_title, news_paragraph = nasa_mars_news(browser)

    # Set up data dictionary for scraping
    data = {
        "page_title": page_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "hemispheres_urls": hemispheres_urls(browser),
        "mars_weather": twitter_weather(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now()
    }

    # Quit browser and return dictionary
    browser.quit()
    return data


def nasa_mars_news(browser):
    url = "https://mars.nasa.gov/news/"
    browser.visit(url)

    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=0.5)

    html = browser.html
    soup = BeautifulSoup(html, "html.parser")

    slide = soup.select_one("ul.item_list li.slide")
    page_title = slide.find("div", class_="content_title").get_text()
    paragraph = slide.find(
    "div", class_="article_teaser_body").get_text()

    return page_title, paragraph


def featured_image(browser):
    url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    browser.visit(url)

    featured_image_url= browser.find_by_id("full_image")
    featured_image_url.click()

    browser.is_element_present_by_text("more info", wait_time=0.5)
    more_info = browser.find_link_by_partial_text("more info")
    more_info.click()

    html = browser.html
    image_soup = BeautifulSoup(html, "html.parser")

    relative_image = image_soup.select_one("figure.lede a img")

    relative_image_url = relative_image.get("src")

    image_url = f"https://www.jpl.nasa.gov{relative_image_url}"

    return image_url


def hemispheres_urls(browser):

    url = (
        "https://astrogeology.usgs.gov/search/"
        "results?q=hemisphere+enhanced&k1=target&v1=Mars"
    )

    browser.visit(url)

    hemispheres_urls = []
    for i in range(4):

        browser.find_by_css("a.product-item h3")[i].click()

        hemisphere_data = scrape_hemisphere(browser.html)
        hemispheres_urls.append(hemisphere_data)

        # go back in the browser
        browser.back()

    return hemispheres_urls


def twitter_weather(browser):
    url = "https://twitter.com/marswxreport?lang=en"
    browser.visit(url)

    html = browser.html
    weather_soup = BeautifulSoup(html, "html.parser")

    tweet_attrs = {"class": "tweet", "data-name": "Mars Weather"}
    weather_tweet = weather_soup.find("div", attrs=tweet_attrs)

    mars_weather = weather_tweet.find("p", "tweet-text").get_text()

    return mars_weather


def scrape_hemisphere(html_text):

    hemisphere_soup = BeautifulSoup(html_text, "html.parser")

    image_title = hemisphere_soup.find("h2", class_="title").get_text()
    sample_image = hemisphere_soup.find("a", text="Sample").get("href")

    hemisphere = {
        "title": image_title,
        "img_url": sample_image
    }

    return hemisphere


def mars_facts():

    df = pd.read_html("http://space-facts.com/mars/")[0]

    df.columns = ["description", "value","value2"]
    df.set_index("description", inplace=True)

    return df.to_html(classes="table table-striped")


if __name__ == "__main__":

    print(scrape_all())
  