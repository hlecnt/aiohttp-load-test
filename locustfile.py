from time import sleep

from locust import HttpUser, SequentialTaskSet, between, task, events


class FloodSequence(SequentialTaskSet):
    @task
    def ping(self):
        self.client.get(f"/ping")


class FloodUser(HttpUser):
    tasks = [FloodSequence]
    # host = "https://docs.locust.io/en/latest/"
    wait_time = between(0.1, 0.5)


@events.init.add_listener
def on_locust_init(environment, **_kwargs):
    sleep(5)
