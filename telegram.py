"""
TODO
"""

from https_requests import HTTPSRequest
from private.config import TelegramPrivate
from sender import Sender


class Telegram(Sender):
    """
    TODO
    """

    def __init__(self, bot_api_key: str, channel_id: str = None):
        self.base_url = "https://api.telegram.org"
        self.bot_api_key = bot_api_key
        self.channel_id = channel_id

    def __message_url(self, message: str, channel_id: str = None):
        url = f"{self.base_url}/bot{self.bot_api_key}/sendMessage?chat_id="
        if channel_id is None:
            return url + f"{self.channel_id}&parse_mode=MarkdownV2&text={message}"
        else:
            return url + f"{channel_id}&parse_mode=MarkdownV2&text={message}"

    def send_message(self, message: str, destination_id: str = None):
        url = self.__message_url(message, destination_id)
        print(url)
        response = HTTPSRequest().get_request(url)
        print(response)

    def login(self, user_name: str = None, password: str = None) -> bool:
        return True


if __name__ == "__main__":
    print("Start Telegram")
    telegram = Telegram(TelegramPrivate.bot_api_key, TelegramPrivate.channel_id)
    telegram.send_message("__Hello__ *World*  ~from~ _Joshua_ 🥇\n🥈🥉👎👍👌⛔️❌❗️‼️💡🥴")
    telegram.send_message("[Mas información](https://www.google.com/)")
    print("End Telegram")
