import re
import requests
import json
import time
from fake_useragent import UserAgent

ua = UserAgent()

# Construct wiki page url
def wiki_to_uri(url, subreddit):
    return f"https://www.reddit.com/r/{subreddit}/wiki/{url}"

# Perform request with fake UserAgent
def fake_ua_get(url):
    return requests.get(url,headers={'User-Agent':ua.random})

# Get a url and raise if the request fails
def get_and_raise(url):
    req = fake_ua_get(url)
    req.raise_for_status()
    return req

# Extract MD from a wiki page json
def extract_md(data):
    return json.loads(data)['data']['content_md']

# Appends .json to a url, downloads it, and extracts the
# MD out of the json file
def get_wiki_md(url):
    url = f"{url}.json"
    req = get_and_raise(url)
    return extract_md(req.text)

# Parse categories from the "national_archives" page
def parse_na(md):
    regex = re.compile(r"###([^\n]+)")
    match = regex.search(md)
    post = match.string[match.end():] # Post-match string
    cat_match = regex.search(post) # Match until the beginning of the next categoru
    # If there is no next category, return text until the end of categories all together
    # Else, return the piece between this and the next category
    if cat_match == None:
        return [[match[1],re.split(r'\*\*\*', post)[0]]]
    else:
        return [[match[1],post[:cat_match.start()]]] + parse_na(post)

# Parse the National Archives amendment tags
# into amendment objects
def parse_amendments(amend_str):
    return list(map(parse_amendment_str, amend_str.split(' '))) if amend_str is not None else []

# Parse one amendment tag
# into an amendment object
def parse_amendment_str(amend_str):
    return (lambda m: m[1]
           )(re.search(r'\(([^)]+)\)',amend_str))

# Parse the date of enactment
# From a human-readable format
# Into a time struct
def parse_enact_date(date):
    return time.strptime(date, '%d/%m/%Y') if date is not None else None

# Parse one category from text
# To a list of laws (and amendments)
def parse_category(category):
    regex = re.compile(r'\* (\[.*\])? ?\[([^\]]+)\] ?\(([^)]+)\)(?:[ \-–]+[^0-9()\n]*(\d+\/\d+\/\d+))?[^()\n]*')
    return [category[0],list(map(
        lambda m:
            [m[2],m[3],parse_enact_date(m[4]), parse_amendments(m[1])],
        regex.finditer(category[1])
    ))]

# Parse the list of categories to turn each category
# from text into a list of laws
def parse_categories(categories):
    return list(map(parse_category, categories))

if __name__ == "__main__":
    sub = "SimDemocracy"
    url = wiki_to_uri("national_archives", sub)
    md = get_wiki_md(url)
    categories = parse_na(md)
    print(json.dumps(parse_categories(categories), indent=2))
    # parse_categories(categories)



