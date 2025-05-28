from typing import Optional
import sys
import asyncio

from playwright.async_api import BrowserContext,Page
from tenacity import (RetryError, retry, retry_if_result, stop_after_attempt,
                      wait_fixed)

from base.base_crawler import AbstractLogin
import config
from tools import crawler_utils as utils

class BilibiliLogin(AbstractLogin):
    def __init__(self,
                 login_type: str,
                 browser_context: BrowserContext,
                 context_page: Page,
                 login_phone: Optional[str]="",
                 cookie_str: str = ""):
        config.LOGIN_TYPE = login_type
        self.browser_context = browser_context
        self.context_page = context_page
        self.login_phone = login_phone
        self.cookie_str = cookie_str

    async def begin(self):
        if config.LOGIN_TYPE == "qrcode":
            await self.login_by_qrcode()
        elif config.LOGIN_TYPE == "phone":
            await self.login_by_mobile()
        elif config.LOGIN_TYPE == "cookie":
            await self.login_by_cookies()
        elif config.LOGIN_TYPE == "manual":
            await self.login_by_manual()
        else:
            raise ValueError(
                "[BilibiliLogin.begin] Invalid Login Type Currently only supported qrcode or phone or cookie ...")

    @retry(stop=stop_after_attempt(600), wait=wait_fixed(1), retry=retry_if_result(lambda value: value is False))
    async def check_login_state(self) -> bool:
        """
            Check if the current login status is successful and return True otherwise return False
            retry decorator will retry 20 times if the return value is False, and the retry interval is 1 second
            if max retry times reached, raise RetryError
        """
        current_cookie = await self.browser_context.cookies()
        _, cookie_dict = utils.convert_cookies(current_cookie)
        if cookie_dict.get("SESSDATA", "") or cookie_dict.get("DedeUserID"):
            return True
        return False

    async def login_by_manual(self):
        i = input("[BilibiliLogin.manual] Please login manually and press [Y/y] key to continue ...\ninput: ")
        if i == "Y" or i == "y":
            try:
                await self.check_login_state()
            except RetryError:
                print("[BilibiliLogin.login_by_qrcode] Login bilibili failed by manual login method ...")
                sys.exit()
            wait_redirect_seconds = 5
            print(
                f"[BilibiliLogin.login_by_qrcode] Login successful then wait for {wait_redirect_seconds} seconds redirect ...")
            await asyncio.sleep(wait_redirect_seconds)

        else:
            raise ValueError("[BilibiliLogin.manual] Please login manually and press [Y] key to continue ...")

    async def login_by_qrcode(self):
            pass

    async def login_by_mobile(self):
        pass

    async def login_by_cookies(self):
        pass

