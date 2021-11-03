from fastapi import FastAPI
import json

from fake_floater.fake_floater import FakeFloater

app = FastAPI()

floaters = {}

with open('fake_floaters.json', 'r') as json_file:
    data = json.load(json_file)

    for floater in data:
        floaters[floater] = FakeFloater(
            mac_address=data[floater]["mac_address"],
            starting_position=data[floater]["starting_position"])

        floaters[floater].start()


@app.get("/")
def read_root():
    return {"online": "true!"}
