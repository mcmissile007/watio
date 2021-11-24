
'''
TODO
'''
import datetime


def is_night(_datetime): 
    if _datetime.hour >= 0 and _datetime.hour <= 6:
        return True
    return False

def is_morning(_datetime):
    if _datetime.hour >= 7 and _datetime.hour <= 12:
        return True
    return False

def is_afternoon(_datetime):
    if _datetime.hour >= 13 and _datetime.hour <= 18:
        return True
    return False

def is_evening(_datetime):
    if _datetime.hour >= 19 and _datetime.hour <= 23:
        return True
    return False


results = [(datetime.datetime(2021, 11, 24, 15, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))), 0.1881018602952125), (datetime.datetime(2021, 11, 24, 14, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))), 0.19433609337928243), (datetime.datetime(2021, 11, 24, 23, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))), 0.19512432974623373), (datetime.datetime(2021, 11, 24, 16, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))), 0.19842059091712128), (datetime.datetime(2021, 11, 24, 22, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))), 0.20157353638492675), (datetime.datetime(2021, 11, 24, 17, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))), 0.20780776946899668), (datetime.datetime(2021, 11, 24, 13, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))), 0.21275216122532797), (datetime.datetime(2021, 11, 24, 12, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))), 0.21733826372395412), (datetime.datetime(2021, 11, 24, 18, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))), 0.22794362575202703), (datetime.datetime(2021, 11, 24, 21, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))), 0.2294484406343887), (datetime.datetime(2021, 11, 24, 19, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))), 0.2351810687576714), (datetime.datetime(2021, 11, 24, 20, 0, tzinfo=datetime.timezone(datetime.timedelta(seconds=3600))), 0.23869230348318202)]

for result in results:
    print(result)
    print()

results_night = [item for item in results if is_night(item[0])]
results_night.sort(key=lambda item: item[1])

results_morning = [item for item in results if is_morning(item[0])]
results_morning.sort(key=lambda item: item[1])

results_afternoon = [item for item in results if is_afternoon(item[0])]
results_afternoon.sort(key=lambda item: item[1])

results_evening = [item for item in results if is_evening(item[0])]
results_evening.sort(key=lambda item: item[1])

print(results_afternoon)









