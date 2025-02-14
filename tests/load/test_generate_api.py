from locust import HttpUser, task, between
import time
import random

# Define our test cases
test_cases = [
    {"prompt": "Once upon a time, in a galaxy far away "},
    {"prompt": "Roses are red, violets are "},
    {"prompt": "Breaking News: Scientists discover "},
    {"prompt": "Thank you for contacting customer support. How can I assist you with your "},
    {"prompt": "Today's weather is perfect for "},
    {"prompt": "I'm having trouble with my computer it keeps "},
    {"prompt": "The book is on the "},
    {"prompt": "In a world where magic is forbidden, a young wizard must "},
    {"prompt": "In the year 1789, during the French Revolution, "},
    {"prompt": "According to the new amendment, the rights of the accused include "},
    {"prompt": "As a grumpy old man, I would say "},
]

class GenerateApiLoadTest(HttpUser):
    wait_time = between(1, 2)  # Wait between 1 and 2 seconds between tasks

    @task
    def generate_text(self):
        # randomly choose a test case to avoid bias in multi-user scenarios
        case = random.choice(test_cases)
        start_time = time.time()

        try:
            response = self.client.post("/generate", json=case, name="/generate")
            response_time = (time.time() - start_time) * 1000  # convert to milliseconds

            if response.status_code == 200:
                self.environment.events.request.fire(
                    request_type = "POST",
                    name = "/generate",
                    response_time = response_time,
                    response_length = len(response.content),
                    context = {"status_code": response.status_code}
                )
                print(f"Successful response for input: {case['prompt']}. Time: {response_time:.2f}ms")
            else:
                self.environment.events.request.fire(
                    request_type = "POST",
                    name = "/generate",
                    response_time = response_time,
                    response_length = len(response.content),
                    exception = Exception(f"Non-200 status code: {response.status_code}"),
                    context = {"status_code": response.status_code}
                )
                print(f"Failed response for input: {case['prompt']}. Status code: {response.status_code}")

        except Exception as e:
            response_time = (time.time() - start_time) * 1000  # convert to milliseconds
            self.environment.events.request.fire(
                request_type = "POST",
                name = "/generate",
                response_time = response_time,
                exception = e
            )
            print(f"Error for input: {case['prompt']}. Time: {response_time:.2f}ms. Error: {str(e)}")