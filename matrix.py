"""
TODO
"""
from dataclasses import dataclass
import json
import requests


@dataclass
class Matrix:
    """
    TODO
    """

    client_base_url: str = ""
    media_base_url: str = ""
    user_name: str = ""
    password: str = ""
    user_id: tuple = (None,)
    home_server: tuple = (None,)
    access_token: tuple = (None,)
    room_id: tuple = None

    def is_supported_login_password(self):
        """
        TODO
        """
        try:
            response = requests.get(self.client_base_url + "login")
            if response.status_code != 200:
                return False
            response = response.json()
            for flow in response["flows"]:
                if flow["type"] == "m.login.password":
                    return True
            return False
        except (
            requests.RequestException,
            requests.ConnectionError,
            requests.HTTPError,
        ) as error:
            print(f"Request post exception: {error}")
            return False
        except json.JSONDecodeError as error:
            print(f"JSON error: {error}")
            return False

    def register(self):
        """
        TODO
        """
        if not self.is_supported_login_password():
            return False
        post_data = {
            "username": self.user_name,
            "password": self.password,
            "auth": {"type": "m.login.password"},
        }
        try:
            response = requests.post(
                self.client_base_url + "register", data=json.dumps(post_data)
            )
            if response.status_code != 200:
                return False
            response = response.json()
            if "user_id" in response:
                self.user_id = response["user_id"]
            else:
                return False
            if "access_token" in response:
                self.access_token = response["access_token"]
            else:
                return False
            if "home_server" in response:
                self.home_server = response["home_server"]
            else:
                return False
            return True
        except (
            requests.RequestException,
            requests.ConnectionError,
            requests.HTTPError,
        ) as error:
            print(f"Request post exception: {error}")
            return False
        except json.JSONDecodeError as error:
            print(f"Exception: {error}")
            return False

    def login(self):
        """
        TODO
        """
        if not self.is_supported_login_password():
            print("Not supported login password")
            return False
        post_data = {
            "user": self.user_name,
            "password": self.password,
            "type": "m.login.password",
        }
        try:
            response = requests.post(
                self.client_base_url + "login", data=json.dumps(post_data)
            )
            if response.status_code != 200:
                return False
            response = response.json()
            if "user_id" in response:
                self.user_id = response["user_id"]
            else:
                return False
            if "access_token" in response:
                self.access_token = response["access_token"]
            else:
                return False
            if "home_server" in response:
                self.home_server = response["home_server"]
            else:
                return False
            return True
        except (
            requests.RequestException,
            requests.ConnectionError,
            requests.HTTPError,
        ) as error:
            print(f"Request post exception: {error}")
            return False
        except json.JSONDecodeError as error:
            print(f"Exception: {error}")
            return False

    def create_room(self, alias_name, name, topic):
        """
        TODO
        """
        if self.access_token is None:
            return False
        post_data = {
            "preset": "private_chat",
            "room_alias_name": alias_name,
            "name": name,
            "topic": topic,
            "creation_content": {"m.federate": False},
        }
        try:
            response = requests.post(
                self.client_base_url + "createRoom?access_token=" + self.access_token,
                data=json.dumps(post_data),
            )
            if response.status_code != 200:
                return False
            response = response.json()
            if "room_id" in response:
                self.room_id = response["room_id"]
            else:
                return False
            return True
        except (
            requests.RequestException,
            requests.ConnectionError,
            requests.HTTPError,
        ) as error:
            print(f"Request post exception: {error}")
            return False
        except json.JSONDecodeError as error:
            print(f"Exception: {error}")
            return False

    def invite_user_to_room(self, user_id, room_id=None):
        """
        TODO
        """
        if self.access_token is None:
            return False
        if room_id is None and self.room_id is None:
            return False
        if room_id is None and self.room_id is not None:
            room_id = self.room_id
        post_data = {"user_id": user_id}
        try:
            response = requests.post(
                self.client_base_url
                + "rooms/"
                + room_id
                + "/invite?access_token="
                + self.access_token,
                data=json.dumps(post_data),
            )
            if response.status_code != 200:
                return False
            return True
        except (
            requests.RequestException,
            requests.ConnectionError,
            requests.HTTPError,
        ) as error:
            print(f"Request post exception: {error}")
            return False

    def send_message(self, message, room_id=None):
        """
        TODO
        """
        if self.access_token is None:
            return False
        if room_id is None and self.room_id is None:
            return False
        if room_id is None and self.room_id is not None:
            room_id = self.room_id
        post_data = {"msgtype": "m.text", "body": message}
        try:
            response = requests.post(
                self.client_base_url
                + "rooms/"
                + room_id
                + "/send/m.room.message?access_token="
                + self.access_token,
                data=json.dumps(post_data),
            )
            if response.status_code != 200:
                return False
            return True
        except (
            requests.RequestException,
            requests.ConnectionError,
            requests.HTTPError,
        ) as error:
            print(f"Request post exception: {error}")
            return False

    def send_preloaded_image(self, file_name, content_uri, room_id=None):
        """
        TODO
        """
        if self.access_token is None:
            return False
        if room_id is None and self.room_id is None:
            return False
        if room_id is None and self.room_id is not None:
            room_id = self.room_id
        post_data = {"msgtype": "m.image", "body": file_name, "url": content_uri}
        try:
            response = requests.post(
                self.client_base_url
                + "rooms/"
                + room_id
                + "/send/m.room.message?access_token="
                + self.access_token,
                data=json.dumps(post_data),
            )
            if response.status_code != 200:
                return False
            return True
        except (
            requests.RequestException,
            requests.ConnectionError,
            requests.HTTPError,
        ) as error:
            print(f"Request post exception: {error}")
            return False

    def send_image(self, image_file_name, room_id=None):
        """
        TODO
        """
        if self.access_token is None:
            return False
        if room_id is None and self.room_id is None:
            return False
        if room_id is None and self.room_id is not None:
            room_id = self.room_id
        # first upload image
        try:
            with open(image_file_name, "rb") as file:
                data = file.read()
                headers = {"Content-Type": "image/png"}
                url = (
                    self.media_base_url
                    + "upload?filename="
                    + image_file_name
                    + "&access_token="
                    + self.access_token
                )
                try:
                    print(url)
                    response_image_upload = requests.post(
                        url, data=data, headers=headers
                    )
                    if response_image_upload.status_code != 200:
                        print(
                            "Error from server to upload image: code->{} content->{}".format(
                                response_image_upload.status_code,
                                response_image_upload.content,
                            )
                        )
                        return False
                    response_image_upload = response_image_upload.json()
                    if "content_uri" in response_image_upload:
                        return self.send_preloaded_image(
                            image_file_name, response_image_upload["content_uri"]
                        )

                    print(f"Error in response:{response_image_upload}")
                    return False

                except (
                    requests.RequestException,
                    requests.ConnectionError,
                    requests.HTTPError,
                ) as error:
                    print(f"Request post exception: {error}")
                    return False
                except json.JSONDecodeError as error:
                    print(f"Exception: {error}")
                    return False
        except OSError as error:
            print(f"OSError Exception: {error}")
            return False

        return False
