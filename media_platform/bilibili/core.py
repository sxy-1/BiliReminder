# 导入
import asyncio
from asyncio import Semaphore
import os
import sys
import random

from playwright.async_api import (BrowserContext, BrowserType, Page, async_playwright, Response)
from typing import Dict, List, Optional, Tuple

import config
from tools import utils
from .client import BilibiliClient
from .login import BilibiliLogin
from base.base_crawler import AbstractCrawler


class BilibiliCrawler(AbstractCrawler):
    def __init__(self):
        self.index_url = "https://www.bilibili.com"
        self.user_agent = utils.get_user_agent()

    async def start(self) -> None:
        playwright_proxy_format, httpx_proxy_format = None, None

        async with async_playwright() as playwright:
            # Launch a browser context. 启动浏览器上下文
            chromium = playwright.chromium
            ua = utils.get_user_agent()
            self.browser_context = await self.launch_browser(chromium, None, ua, config.HEADER_LESS)
            await self.browser_context.add_init_script(path="libs/stealth.min.js")
            self.context_page = await self.browser_context.new_page()
            await self.context_page.goto(self.index_url)

            # Create a client to interact with the xiaohongshu website.
            # self.bili_client = await self.create_bilibili_client(httpx_proxy_format)
            # if not await self.bili_client.pong():
            #     login_obj = BilibiliLogin(
            #         login_type=config.LOGIN_TYPE,
            #         login_phone="",  # your phone number
            #         browser_context=self.browser_context,
            #         context_page=self.context_page,
            #         cookie_str=config.COOKIES
            #     )
            #     await login_obj.begin()
            #     await self.bili_client.update_cookies(browser_context=self.browser_context)

            utils.logger.info("Start")
            await self.search()
            utils.logger.info("End")
    async def launch_browser(self, chromium: BrowserType, playwright_proxy: Optional[Dict], user_agent: Optional[str],
                             headless: bool = True) -> BrowserContext:
        """Launch browser and create browser context"""
        # we will save login state to avoid login every time
        if config.SAVE_LOGIN_STATE:
            user_data_dir = os.path.join(os.getcwd(), "browser_data",
                                         config.USER_DATA_DIR % config.PLATFORM)  # type: ignore

            # launch browser context
            browser_context = await chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                accept_downloads=True,
                headless=headless,
                proxy=playwright_proxy,  # type: ignore
                viewport={"width": 1920, "height": 1080},
                user_agent=user_agent
            )
            return browser_context
        else:
            # type: ignore
            browser = await chromium.launch(headless=headless, proxy=playwright_proxy)
            browser_context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent=user_agent
            )
            return browser_context

    async def create_bilibili_client(self, httpx_proxy: Optional[str]) -> BilibiliClient:
        cookie_str, cookie_dict = utils.convert_cookies(await self.browser_context.cookies())
        bilibili_client_obj = BilibiliClient(
            proxies=httpx_proxy,
            headers={
                "User-Agent": self.user_agent,
                "Cookie": cookie_str,
                "Origin": "https://www.bilibili.com",
                "Referer": "https://www.bilibili.com",
                "Content-Type": "application/json;charset=UTF-8"
            },
            playwright_page=self.context_page,
            cookie_dict=cookie_dict,
        )
        return bilibili_client_obj

    async def search(self) -> None:
        """Task execution function"""
        await self.context_page.fill('xpath=//*[@id="nav-searchform"]/div[1]/input', config.KEYWORDS)
        async with self.browser_context.expect_page() as new_page_info:
            await self.context_page.click('xpath=//*[@id="nav-searchform"]/div[2]')
        new_page1 = await new_page_info.value

        '''
        async with self.browser_context.expect_page() as new_page_info:
            await new_page1.click('xpath=//*[@id="i_cecream"]/div/div[2]/div[2]/div/div/div/div[3]/div/div[1]')
        new_page2 = await new_page_info.value

        new_page2.on("response",self.page_on)
        likes = await new_page2.text_content('xpath=//span[@class="video-like-info video-toolbar-item-text"]')
        coins = await new_page2.text_content('xpath=//span[@class="video-coin-info video-toolbar-item-text"]')
        favs = await new_page2.text_content('xpath=//span[@class="video-fav-info video-toolbar-item-text"]')
        shares = await new_page2.text_content('xpath=//span[@class="video-share-info-text"]')
        await new_page2.mouse.wheel(0, 1000)
        utils.logger.info(fr"{likes} {coins} {favs} {shares}")
        '''

        await new_page1.wait_for_load_state('networkidle')  # 等待网络空闲
        a_list = await new_page1.query_selector_all('xpath=//div[@class="video-list row"]//a')
        href_list = []
        for a in a_list:
            href = await a.get_attribute("href")
            if 'video' in href:
                href_list.append(href)
        utils.logger.warn(f"href_count: {len(href_list)}")
        if len(href_list) == 0:exit(1)
        semaphore = asyncio.Semaphore(5)
        tasks = [asyncio.create_task(self.get_video_detail(href, semaphore)) for href in href_list]
        await asyncio.gather(*tasks)

    async def get_video_detail(self, href: Optional[str], semaphore:Semaphore) -> None:
        if href is None:
            return
        if not href.startswith('https:'):
            href = 'https:' + href

        """get detail data"""
        async with semaphore:
            page = await self.browser_context.new_page()
            await page.goto(href)
            page.on("response", self.page_on)
            likes = await page.text_content('xpath=//span[@class="video-like-info video-toolbar-item-text"]')
            coins = await page.text_content('xpath=//span[@class="video-coin-info video-toolbar-item-text"]')
            favs = await page.text_content('xpath=//span[@class="video-fav-info video-toolbar-item-text"]')
            shares = await page.text_content('xpath=//span[@class="video-share-info-text"]')
            utils.logger.info(fr"{likes} {coins} {favs} {shares}")

            await self.mouse_wheel(page, 5)
            await page.close()

    async def page_on(self, response: Response) -> None:
        """page on Response to Get comments"""
        url = response.url
        if 'x/v2/reply/wbi/main' in url:
            json_data = await response.json()
            data = json_data.get('data', [])
            if len(data) == 0:
                utils.logger.info("get comments failed...")
                return
            replies = data.get('replies', [])
            if len(replies) == 0:
                utils.logger.info("The comments are empty...")
                return
            for r in replies:
                rname = r['member']['uname']
                rId = r['rpid']
                content = r['content']['message']
                utils.logger.info(fr"{rname} {rId} {content}")

    async def mouse_wheel(self, page: Page, count: int) -> None:
        """mouse wheel"""
        all_px = random.randint(500, 1000)
        for i in range(count):
            sub_px = 0
            while sub_px < all_px:
                px = random.randint(100, 300)
                await page.mouse.wheel(0, px)
                sub_px += random.randint(100, 300)
                await asyncio.sleep(random.uniform(0.1, 0.5))
            await asyncio.sleep(random.randint(1, 3))

