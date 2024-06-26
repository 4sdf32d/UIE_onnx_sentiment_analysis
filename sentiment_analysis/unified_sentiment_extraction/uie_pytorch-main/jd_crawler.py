import random
import requests
import json
import time
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

class JDCrawler:
    def __init__(self, keyword, filename_func):
        self.keyword = keyword
        self.filename = filename_func(keyword)
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/97.0.1072.62",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36 Edg/96.0.1054.57",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 YaBrowser/22.2.2.127 Yowser/2.5 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Whale/2.11.125.18 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
            # 添加更多用户代理
        ]

    def start(self, page, produce_id):
        url = ('https://club.jd.com/comment/productPageComments.action?'
               f'&productId={produce_id}'
               f'&score=0'
               '&sortType=5'
               f'&page={page}'
               '&pageSize=10'
               '&isShadowSku=0'
               '&fold=1')

        headers = {
            "User-Agent": random.choice(self.user_agents)  # 随机选择用户代理
        }

        response = requests.get(url=url, headers=headers)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data
        else:
            print(f"Failed to fetch data for product ID {produce_id}, status code: {response.status_code}")
            return None

    def parse(self, data):
        if 'comments' in data:
            items = data['comments']
            for i in items:
                yield i.get('content', '')

    def read_first_column(self, line):
        return line.split(',')[0]

    def crawl(self):
        df = pd.read_csv(self.filename, encoding='utf-8-sig', header=None, converters={0: self.read_first_column})
        produce_ids = df.iloc[:, 0].tolist()

        all_comments = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for produce_id in produce_ids:
                total_pages = 1  # 这里应该根据实际情况获取总页数
                for current_page in range(total_pages):
                    futures.append(executor.submit(self.fetch_comments, current_page + 1, produce_id))
                    time.sleep(random.uniform(0.5, 1.5))  # 随机延迟，避免被检测
            for future in as_completed(futures):
                parsed_data = future.result()
                if parsed_data:
                    all_comments.extend(parsed_data)

        return all_comments

    def fetch_comments(self, page, produce_id):
        data = self.start(page, produce_id)
        if data:
            return list(self.parse(data))
        else:
            return []
