import datetime
import sched

from common.send_dingplus import get_access_token


def get_token(schedule, sec, app):
    token = get_access_token()
    print(
        "[GET TOKEN]",
        datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
        token,
    )
    app.config["TOKEN"] = token
    schedule.enter(sec, 1, get_token, (schedule, sec, app))


def process_get_token(app):
    sec = 3600
    schedule = sched.scheduler()
    schedule.enter(sec, 1, get_token, (schedule, sec, app))
    schedule.run()
