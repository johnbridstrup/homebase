# Home Base API

This is a basic app for adding and tracking IoT devices in a home. The initial focus is on sensors
but it could evolve to include controls. I'm not sure if I plan on writing a frontend app for this or
not, as the idea is to dynamically add sensors as needed. I may make a rudimentary one with Flask/Dash.

## Main idea

Sensors identify themselves with HTTP using a payload like this
```json
{
    "identifier": "Some Unique ID from the device",
    "sensor_type": "temperature/humidity/proximity",
}
```

and then subequently post, at whatever frequency, payloads like this:
```json
{
    "identifier": "The same unique ID",
    "data": {
        "temperature": 98.6,
        "something else": 69420,
    }
}
```

They can register and post freely without auth, but will only begin populating the database with data after a user marks them as active.