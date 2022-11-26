# Mongodb Testing
This script was created to test connecting, reading and writing data to a mongodb cluster.
Identification of performance and infrastructure problem areas.

## Requirements
- [pymongo 4.3.3](https://pypi.org/project/pymongo/)

## Example
```sh
# Testing read data in collection mongodb
python3 mongodb-testing.py read
# Testing write data in collection mongodb
python3 mongodb-testing.py write
```