from locust import HttpUser, task

class HelloWorldUser(HttpUser):
    @task
    def hello_world(self):
        self.client.get("/")
        self.client.get("/users")
        self.client.get("/scoreboard")
        self.client.get("/challenges")
        self.client.get("/login")
        self.client.post(url = 'https://fierce-garden-25525.herokuapp.com/login?next=/challenges?',
                    json = {"name" : "test", "password": "test", "_submit": "Submit", "nonce": "9272af98535de548a708f87730ec95519fa4bf5152ef5334b770f5cbdcb7437c"}    )