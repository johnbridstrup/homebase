# A utility for spawning mock sensors to send data to the server
import argparse, random, uuid
import asyncio
from aiohttp import ClientSession

class Sensor:
    def __init__(self, sensor_type: str, url: str, session: ClientSession, f, init_=0):
        self.identifier = str(uuid.uuid4())
        self.sensor_type = sensor_type
        self.session = session
        self.url = url
        self.gen_data = f
        self.last = init_

    async def register(self):
        async with self.session.post(f"{self.url}/sensors/", json={"identifier": self.identifier, "sensor_type": self.sensor_type}) as response:
            if not response.status in [200, 201]:
                print("failed to register")

    async def post_data(self):
        data, self.last = self.gen_data(self.last)
        async with self.session.post(f"{self.url}/sensordata/", json={"identifier": self.identifier, "data": data}) as response:
            if not response.status in [201, 403]:
                print(f"Failed to post data: {response}")

    def __str__(self):
        return f"Sensor {self.identifier} ({self.sensor_type})"
    
def _gen_brownian(stype, seed):
    t = seed + random.randint(-1, 1)
    return {stype: t}, t

def _gen_binary(stype, seed):
    r = random.random()
    if r < 0.1:
        b = int(not bool(seed)) # favor not changing
    else:
        b = int(seed)
    return {stype: b}, b

sensor_types = {
    "temperature": lambda seed: _gen_brownian("temperature", seed),
    "door": lambda seed: _gen_binary("door", seed),
}

parser = argparse.ArgumentParser(description="Spawn sensors to send data to the server")
parser.add_argument("--url", type=str, help="URL of the server")
parser.add_argument("--sensors", nargs="+", type=str, help="Types of sensors to spawn", choices=sensor_types.keys())

async def main():
    args = parser.parse_args()
    url = args.url
    sensors = args.sensors
    if not url or not sensors:
        parser.print_help()
        return
    async with ClientSession() as session:
        sensor_objs = [Sensor(sensor_type, url, session, sensor_types[sensor_type]) for sensor_type in sensors]
        await asyncio.gather(*[sensor.register() for sensor in sensor_objs])
        while True:
            try:
                await asyncio.gather(*[sensor.post_data() for sensor in sensor_objs])
                await asyncio.sleep(random.randint(5, 10))
            except KeyboardInterrupt:
                break

if __name__ == "__main__":
    asyncio.run(main())
