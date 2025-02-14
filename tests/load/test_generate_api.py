from locust import HttpUser, task, between
import time
import random

# Define our test cases
test_cases = [
    {"prompt": "Once upon a time, in galaxy far away "},
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
        # Cycle through our test cases
        # Randomly choose a test case to avoid sequential bias in multi-user scenarios
        case = random.choice(test_cases)
        start_time = time.time()
        
        try:
            response = self.client.post("/generate", json=case, name="/generate")
            response_time = time.time() - start_time
            self.environment.events.request_success.fire(
                request_type="POST",
                name="/generate",
                response_time=response_time * 1000,  # Convert to milliseconds
                response_length=len(response.content)
            )
            print(f"Successful response for input: {case}. Time: {response_time:.2f}s")
        except Exception as e:
            response_time = time.time() - start_time
            self.environment.events.request_failure.fire(
                request_type="POST",
                name="/generate",
                response_time=response_time * 1000,  # Convert to milliseconds
                exception=str(e)
            )
            print(f"Error for input: {case}. Time: {response_time:.2f}s. Error: {str(e)}")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_index = 0  # Keep track of which test case we're on

