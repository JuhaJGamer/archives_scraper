import re
import requests
import json
import time
from fake_useragent import UserAgent

ua = UserAgent()

def get_none(x,i):
    if x is not None:
        return x[i]
    else:
        return x

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

# Get legal text of all laws and amendments in categories
# And add it to the lists
def populate_with_legal_text(categories):
    print(categories)
    return list(map(populate_category, categories))

# Get legal text of all laws and amendments in a category
# And add them to the lists
def populate_category(category):
    print(category)
    return [category[0], list(map(
        (lambda i:
            [i[0], i[1], i[2], populate_amendments(i[3]), parse_legal_text(get_wiki_md(i[1]))]),
        category[1]))]

# Parse the legal text
# Of a law and construct
# A structured version
def parse_legal_text(md):
    return (parse_metadata(md), parse_act(md))

# Parse the metadata found above an act
# And return it as an object
def parse_metadata(md):
    return parse_legislation_specs(
            get_none(re.search(r'##Legislation Specs\n\n((?:.|\n)+)\*\*\*', md),1))

# Parse the 'Legislation Specs' metadata box
def parse_legislation_specs(md):
    return list(map(
        lambda m:
            m[1],
        re.finditer(r'\*\*: ?(.*)', md)
        ))

# Parse the main text of an act
# Into a structured format
def parse_act(md):
    return list(map(
        lambda m:
            [m[1],parse_part(md[m.end():].split('##*')[0])],
        re.finditer(r'^##\*\*(?:Part \d ?[–-] ?)?([^\*]+)',md)
    ))

def parse_part(md):
    return []

if __name__ == "__main__":
    sub = "SimDemocracy"
    url = wiki_to_uri("national_archives", sub)
    md = get_wiki_md(url)
    categories = parse_na(md)
    print(categories)
    categories_parsed = parse_categories(categories)
    print(json.dumps(populate_with_legal_text(categories_parsed), indent=2))
    # parse_categories(categories)



