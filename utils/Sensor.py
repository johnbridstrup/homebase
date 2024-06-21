import argparse, asyncio, random, uuid, yaml
from aiohttp import web, ClientSession
from aiohttp.client_exceptions import ClientConnectionError


class Sensor:
    RPC_INTERFACE = {}

    def __init__(self, port, dest, identifier, sensor_type="generic", **kwargs):
        self._port = port
        self._dest = dest
        self._identifier = identifier
        self._sensor_type = sensor_type
        self._freq = 0.5  # Frequency of data generation in Hz

        self._routes = web.RouteTableDef()
        self._app = web.Application()

        # Routing
        self._setup_rpc_interface()
    
    @classmethod
    def from_config(cls, config):
        return cls(**config)

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
    

class MarkovRandomSensor(Sensor):
    RPC_INTERFACE = {
        "setSampleRate": {"rate": {"type": "number"}},
        "getSampleRate": {},
    }
    
    def __init__(self, *args, **kwargs):
        _init = kwargs.pop("initial_value", 75.0)
        label = kwargs.pop("label", "temperature")
        super().__init__(*args, **kwargs)
        self._init = _init
        self._label = label
    # Abstract method implementation
    def gen_data(self):
        self._init += random.gauss(0, self._freq)
        return {
            "identifier": self._identifier,
            "data": {
                self._label: self._init,
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


parser = argparse.ArgumentParser(description="Spawn sensors to send data to the server")
parser.add_argument("--port", type=int, help="Port to run the sensor server on", default=8080)
parser.add_argument("--dest", type=str, help="URL of the server", default="http://localhost:8000")
parser.add_argument("--identifier", type=str, help="Identifier of the sensor", required=False)
parser.add_argument("--sensor_type", type=str, help="Type of sensor", default="generic")
parser.add_argument("--config", type=str, help="Path to a config file", default=None)


async def main():
    args = parser.parse_args()
    if args.config:
        with open(args.config, 'r') as f:
            config = yaml.safe_load(f)
        sensor = MarkovRandomSensor.from_config(config)
    else:
        conf = {
            "port": args.port,
            "dest": args.dest,
            "sensor_type": args.sensor_type,
            "indentifier": args.identifier or str(uuid.uuid4()),
        }
        
        sensor = MarkovRandomSensor(**conf)
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
