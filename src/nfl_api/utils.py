from datetime import datetime, timezone
# import nfl_api.object
import json


def convert_time(utc_dt):
    local_dt = utc_dt
    local_dt = datetime.strptime(utc_dt, '%Y-%m-%dT%H:%MZ').replace(tzinfo=timezone.utc).astimezone(tz=None)
    return local_dt



