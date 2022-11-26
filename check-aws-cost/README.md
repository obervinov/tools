# Сheck aws cost script
This script is designed to get statistics on the costs of aws services and save this data in kafka for further visualization in grafana.

## Requirements
- [boto3 1.26.16](https://pypi.org/project/boto3/)
- [kafka 1.3.5](https://pypi.org/project/kafka/)

## Example
```sh
# Specify the number of days for unloading
python3 check-aws-cost.py --days 1
```