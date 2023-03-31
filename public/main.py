from parsel import Selector
from playwright.sync_api import sync_playwright
from playwright.sync_api._generated import Page


def parse_tweets(selector: Selector):
    """
    parse tweets from pages containing tweets like:
    - tweet page
    - search page
    - reply page
    - homepage
    returns list of tweets on the page where 1st tweet is the 
    main tweet and the rest are replies
    """
    results = []
    # select all tweets on the page as individual boxes
    # each tweet is stored under <article data-testid="tweet"> box:
    tweets = selector.xpath("//article[@data-testid='tweet']")
    for i, tweet in enumerate(tweets):
        # using data-testid attribute we can get tweet details:
        found = {
            "text": "".join(tweet.xpath(".//*[@data-testid='tweetText']//text()").getall()),
            "username": tweet.xpath(".//*[@data-testid='User-Names']/div[1]//text()").get(),
            "handle": tweet.xpath(".//*[@data-testid='User-Names']/div[2]//text()").get(),
            "datetime": tweet.xpath(".//time/@datetime").get(),
            "verified": bool(tweet.xpath(".//svg[@data-testid='icon-verified']")),
            "url": tweet.xpath(".//time/../@href").get(),
            "image": tweet.xpath(".//*[@data-testid='tweetPhoto']/img/@src").get(),
            "video": tweet.xpath(".//video/@src").get(),
            "video_thumb": tweet.xpath(".//video/@poster").get(),
            "likes": tweet.xpath(".//*[@data-testid='like']//text()").get(),
            "retweets": tweet.xpath(".//*[@data-testid='retweet']//text()").get(),
            "replies": tweet.xpath(".//*[@data-testid='reply']//text()").get(),
            "views": (tweet.xpath(".//*[contains(@aria-label,'Views')]").re("(\d+) Views") or [None])[0],
        }
        # main tweet (not a reply):
        if i == 0:
            found["views"] = tweet.xpath('.//span[contains(text(),"Views")]/../preceding-sibling::div//text()').get()
            found["retweets"] = tweet.xpath('.//a[contains(@href,"retweets")]//text()').get()
            found["quote_tweets"] = tweet.xpath('.//a[contains(@href,"retweets/with_comments")]//text()').get()
            found["likes"] = tweet.xpath('.//a[contains(@href,"likes")]//text()').get()
        results.append({k: v for k, v in found.items() if v is not None})
    return results


def scrape_tweet(url: str, page: Page):
    """
    Scrape tweet and replies from tweet page like:
    https://twitter.com/Scrapfly_dev/status/1587431468141318146
    """
    # go to url
    page.goto(url)
    # wait for content to load
    page.wait_for_selector("//article[@data-testid='tweet']")  
    # retrieve final page HTML:
    html = page.content()
    # parse it for data:
    selector = Selector(html)
    tweets = parse_tweets(selector)
    return tweets


# example run:
with sync_playwright() as pw:
    # start browser and open a new tab:
    browser = pw.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    # scrape tweet and replies:
    tweet_and_replies = scrape_tweet("httpTrutwitter.com/Scrapfly_dev/status/1587431468141318146", page)
    print(tweet_and_replies)