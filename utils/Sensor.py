import asyncio, random
from aiohttp import web, ClientSession
from aiohttp.client_exceptions import ClientConnectionError


class Sensor:
    RPC_INTERFACE = {}

    def __init__(self, port, dest, indentifier, sensor_type="generic"):
        self._port = port
        self._dest = dest
        self._identifier = indentifier
        self._sensor_type = sensor_type
        self._freq = 0.5  # Frequency of data generation in Hz

        self._routes = web.RouteTableDef()
        self._app = web.Application()

        # Routing
        self._setup_rpc_interface()

    # Properties
    @property
    def data_interval(self):
        return 1 / self._freq
    
    @property
    def identity(self):
        return {
            "identifier": self._identifier,
            "sensor_type": self._sensor_type,
            "rpc_interface": self.RPC_INTERFACE,
        }
    
    # Interface
    async def get_site(self):
        runner = web.AppRunner(self._app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', self._port)
        return site
    
    def spawn_task(self):
        return asyncio.create_task(self._post_data())
    
    async def register(self):
        registered = False
        async with ClientSession() as session:
            while not registered:
                try:
                    async with session.post(f"{self._dest}/sensors/", json=self.identity) as response:
                        if response.status in [200, 201]:
                            print("Connected!")
                            registered = True
                        else:
                            print("failed to register")
                            await asyncio.sleep(2)
                            print("retrying...")
                except ClientConnectionError:
                    print("Failed to connect to server")
                    await asyncio.sleep(2)
                    print("retrying...")
    
    
    
    # Internal Methods
    def _setup_rpc_interface(self):
        for k in self.RPC_INTERFACE.keys():
            f = getattr(self, k)
            setattr(self, k, self._routes.post(f'/{k}')(f))
        self._app.add_routes(self._routes)
    
    async def _post_data(self):
        while True:
            print("Sending fake data")
            data = self.gen_data()
            async with ClientSession() as session:
                async with session.post(f"{self._dest}/sensordata/", json=data) as response:
                    if response.status in [200, 201]:
                        print("Data sent successfully")
                    elif response.status == 403:
                        print("Awaiting registration")
                    else:
                        print("Failed to send data")
            await asyncio.sleep(self.data_interval)  # Simulating data

    # Abstract methods
    def gen_data(self):
        raise NotImplementedError("You must implement this method in a subclass")
    

class TemperatureSensor(Sensor):
    RPC_INTERFACE = {
        "setSampleRate": {"rate": {"type": "number"}},
        "getSampleRate": {},
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._temperature = 75.0

    # Abstract method implementation
    def gen_data(self):
        self._temperature += random.gauss(0, self._freq)
        return {
            "identifier": self._identifier,
            "data": {
                "temperature": self._temperature
            }
        }

    # RPC interface
    async def setSampleRate(self, request):
        print("Setting sample rate")
        data = await request.json()
        resp_data = {
            "old_rate": self._freq,
            "new_rate": data["rate"],
        }
        self._freq = data["rate"]
        print(f"Sample rate set to {data['rate']} Hz")
        return web.json_response(resp_data)
    
    async def getSampleRate(self, request):
        print("Getting sample rate")
        return web.json_response({"rate": self._freq})


async def main():
    sensor = TemperatureSensor(8080, "http://localhost:8000", "Test Sensor 3")
    site = await sensor.get_site()
    await site.start()
    print(f"Sensor server running on http://localhost:{sensor._port}")

    # Attempt to register the sensor
    await sensor.register()

    # Spawn the background task
    sensor.spawn_task()

    # Keep the event loop running
    await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())
