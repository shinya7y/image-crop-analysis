import json
import os
import time
import urllib.request
from html.parser import HTMLParser


class GirlsBandParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.found_content = False
        self.content_image = None

    def handle_starttag(self, tag, attrs):
        if tag == 'div' and len(attrs) >= 1:
            if attrs[0][0] == 'class' and attrs[0][1] == 'content':
                self.found_content = True
        elif tag == 'img' and self.found_content:
            for attr in attrs:
                if attr[0] == 'src':
                    assert self.content_image is None
                    self.content_image = attr[1]

    def handle_endtag(self, tag):
        if tag == 'div' and self.found_content:
            self.found_content = False

    def get_content_image(self):
        return self.content_image


def download_manga_images(manga_id, sleep_secs=10, num_limit=10000):
    assert sleep_secs >= 5, 'Wait enough not to increase the server load'
    assert os.path.isdir('data')
    os.makedirs(f'data/{manga_id}', exist_ok=True)

    if manga_id == 'shiny4':
        # download json
        json_url = 'https://shinycolors.idolmaster.jp/api/comic.php'
        json_file = 'data/shiny4.json'
        urllib.request.urlretrieve(json_url, json_file)
        with open(json_file) as f:
            data = json.load(f)
        # download each image
        for epi_data in data[:num_limit]:
            episode = epi_data['order'] - 1  # order 1: 0th episode
            image_url = 'https://shinycolors.idolmaster.jp' + epi_data['comic']
            image_ext = image_url.split('.')[-1].split('?')[0]
            image_path = f'data/{manga_id}/{episode:05d}.{image_ext}'
            print(image_path, image_url)
            urllib.request.urlretrieve(image_url, image_path)
            time.sleep(sleep_secs)

    elif manga_id == 'milli4':
        # download jsonp and save json
        # https://github.com/tankarup/ML-4koma-viewer/blob/main/main.js
        jsonp_url = 'https://script.google.com/macros/s/AKfycby9pjvZZlvKwKp23P8DRyzoXKkR4BWVwW9XHIHElP1M7X4NHaHe5bW2kosqZZ92F4_S/exec'  # noqa
        json_file = 'data/milli4.json'
        if False:
            response = urllib.request.urlopen(jsonp_url)
            res_text = response.read().decode('utf8')
            if res_text[:9] == 'jsondata(':
                res_text = res_text[9:-1]
            data = json.loads(res_text)
            with open(json_file, 'w') as f:
                json.dump(data, f, indent=None, ensure_ascii=False)
        # download each image
        with open(json_file) as f:
            data = json.load(f)
        tweet_urls = [epi_data['URL'] for epi_data in data]
        tweet_ids = [int(url.split('/')[-1]) for url in tweet_urls]
        tweet_ids.sort()
        print(tweet_ids)
        # 'https://twitter.com/imasml_theater/status/'

        # TODO
        raise NotImplementedError

    elif manga_id == 'pri4':
        current_id = 1
        for _ in range(num_limit):
            # download json for each episode
            json_url = ('https://comic.priconne-redive.jp/api/detail/'
                        f'{current_id}')
            response = urllib.request.urlopen(json_url)
            epi_data = json.loads(response.read().decode('utf8'))
            epi_data = epi_data[0]
            # parse data and download image
            next_id = epi_data['next_cartoon']['id']
            episode = int(epi_data['episode_num'])
            image_url = epi_data['cartoon']
            image_ext = image_url.split('.')[-1].split('?')[0]
            image_path = f'data/{manga_id}/{episode:05d}.{image_ext}'
            print(image_path, image_url)
            urllib.request.urlretrieve(image_url, image_path)
            time.sleep(sleep_secs)

            is_latest_episode = epi_data['current_index'] == 0
            if is_latest_episode:
                break
            current_id = next_id

    elif manga_id == 'girl4':
        print('Warning: girl4 episode after 286 not supported')
        num_limit = min(num_limit, 286)
        for episode in range(1, num_limit + 1):
            # download and parse html for each episode
            html_url = ('https://bang-dream.bushimo.jp/special/manga/episode-'
                        f'{episode}')
            response = urllib.request.urlopen(html_url)
            html = response.read().decode('utf8')
            parser = GirlsBandParser()
            parser.feed(html)
            image_url = parser.get_content_image()
            if image_url is None:
                print('not found content_image')
            else:
                # download image
                image_url = urllib.parse.quote(image_url, safe='/:=&%')
                image_ext = image_url.split('.')[-1]
                image_path = f'data/{manga_id}/{episode:05d}.{image_ext}'
                print(image_path, image_url)
                urllib.request.urlretrieve(image_url, image_path)
            time.sleep(sleep_secs)

            # TODO implement termination

    elif manga_id == 'negi4':
        print('Warning: normal-index 1000 negi4 episodes only')
        num_limit = min(num_limit, 1000)
        for episode in range(1, num_limit + 1):
            image_name = f'negi{episode:03d}.jpg'
            image_url = 'http://negineesan.com/comics/negi/' + image_name
            image_ext = image_url.split('.')[-1]
            image_path = f'data/{manga_id}/{episode:05d}.{image_ext}'
            print(image_path, image_url)
            urllib.request.urlretrieve(image_url, image_path)
            time.sleep(sleep_secs)

    else:
        raise NotImplementedError


if __name__ == '__main__':
    manga_ids = ['shiny4', 'pri4', 'girl4', 'negi4']
    for manga_id in manga_ids:
        download_manga_images(manga_id, num_limit=1000)
