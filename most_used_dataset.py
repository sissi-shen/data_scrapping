import sys
from bs4 import BeautifulSoup
import requests

dsURL = "https://catalog.data.gov/dataset?q=&sort=views_recent+desc"

def list_of_pairs(n):
    """ Get first n datasets

    Output: list of (dataset title, url)
    """
    page = 1
    pairs = []
    while True:
        response = requests.get(dsURL + str('&page=') + str(page))
        soup = BeautifulSoup(response.text, 'lxml')
        datasets = soup.find_all('li', class_='dataset-item has-organization')

        for data in datasets:
            urls = data.find('h3', class_='dataset-heading')
            for a in urls.find_all('a', href=True):
                result = []
                title = a.contents[0]
                result.append(title)
                html = a['href']
                result.append(html)

                pairs.append(result)

        if n <= len(pairs):
            break
        else:
            page += 1
    
    return pairs[:n]

if __name__ == "__main__":
    # n = int(sys.argv[1])
    pairs = list_of_pairs(43)
    for title, url in pairs:
        print(title, url)
    print(len(pairs))

