import random

from locust import FastHttpUser, between, task
from locust.exception import StopUser


class QuickstartUser(FastHttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        try:
            self.register_and_login()
        except Exception:
            raise StopUser()

    def register_and_login(self):
        try:
            username = f"user{random.randint(1, 100000)}"
            password = "password"
            register_response = self.client.post(
                "/api/register",
                json={"username": username, "password": password},
            )
            register_response.raise_for_status()

            auth_response = self.client.post(
                "/api/auth",
                data={"username": username, "password": password},
            )
            auth_response.raise_for_status()
            self.token = auth_response.json()["access_token"]
            self.username = username
        except Exception:
            raise StopUser()

    @task
    def buy_item(self):
        try:
            items = ["t-shirt", "cup", "book", "pen", "powerbank"]
            item = random.choice(items)
            buy_response = self.client.post(
                f"/api/buy/{item}",
                headers={"Authorization": f"Bearer {self.token}"},
            )
            buy_response.raise_for_status()
        except Exception:
            pass

    @task
    def send_coin(self):
        try:
            send_response = self.client.post(
                "/api/sendCoin",
                json={"user": self.username, "amount": 10},
                headers={"Authorization": f"Bearer {self.token}"},
            )
            send_response.raise_for_status()
        except Exception:
            pass

    @task
    def get_info(self):
        try:
            info_response = self.client.get(
                "/api/info",
                headers={"Authorization": f"Bearer {self.token}"},
            )
            info_response.raise_for_status()
        except Exception:
            pass
