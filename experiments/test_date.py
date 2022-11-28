#!/usr/bin/env python3

from __future__ import division
from datetime import datetime, timedelta
import pendulum

utc = pendulum.timezone('UTC')

get_log_date = datetime.now(utc) - timedelta(hours=1)
start_date = get_log_date.strftime('%Y-%m-%dT%H:00:00Z')
end_date = datetime.now(utc).strftime('%Y-%m-%dT%H:00:00Z')

print(datetime.now(utc))
print(get_log_date)
print(start_date)
print(end_date)
