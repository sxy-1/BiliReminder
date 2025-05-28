import asyncio
import sys

import cmd_arg
import config
from base.base_crawler import AbstractCrawler
from media_platform.bilibili import BilibiliCrawler


class CrawlerFactory:
    CRAWLERS = {
        "bili": BilibiliCrawler,
    }

    @staticmethod
    def create_crawler(platform: str) -> AbstractCrawler:
        crawler_class = CrawlerFactory.CRAWLERS.get(platform)
        if not crawler_class:
            raise ValueError("Invalid Media Platform Currently only supported bili ...")
        return crawler_class()


async def main():
    # parse cmd
    await cmd_arg.parse_cmd()

    crawler = CrawlerFactory.create_crawler(platform=config.PLATFORM)
    await crawler.start()

if __name__ == '__main__':
    try:
        # asyncio.run(main())
        asyncio.get_event_loop().run_until_complete(main())
    except KeyboardInterrupt:
        sys.exit()
