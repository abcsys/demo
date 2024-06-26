from selectorlib import Extractor
import requests

# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('selectors.yml')


def scrape(url, fake=False):
    if fake:
        return {'name': 'Coke 18 pack (12 Oz Cans) in BGM Ship Safe Box', 'availability': 'In Stock.',
                'price': '$34.99', 'rating': '4.5 out of 5 stars'}

    headers = {
        'authority': 'www.amazon.com',
        'pragma': 'no-cache',
        'cache-control': 'no-cache',
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'none',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-dest': 'document',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    # Download the page using requests
    # print("Downloading %s"%url)
    r = requests.get(url, headers=headers)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n" % url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d" % (url, r.status_code))
        return None
    # Pass the HTML of the page and create
    return e.extract(r.text)


if __name__ == '__main__':
    url = "https://www.amazon.com/Coke-18-pack-12-Cans/dp/B088KPCRD8/"
    data, rows = scrape(url), list()
    print(data)
