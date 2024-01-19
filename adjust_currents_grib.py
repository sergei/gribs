import argparse
import datetime

from grib import Grib
TIDE_DAY_SEC = datetime.timedelta(hours=24, minutes=50).total_seconds()


def make_const_wind_grib(args):
    grib = Grib(args.currents_src_grib, args.work_dir)
    dates = grib.get_dates()
    start_date = datetime.datetime.strptime(args.start_date_utc, '%Y-%m-%d')

    # Find the closest date separated by the integer number of 24 hours and 50 minutes
    delta_sec = (start_date - dates[0]).total_seconds()
    delta_tide_days = delta_sec // TIDE_DAY_SEC
    forward_time_by_sec = delta_tide_days * TIDE_DAY_SEC
    forward_time_by = datetime.timedelta(seconds=forward_time_by_sec)
    dates_map = {}
    for d in dates:
        dates_map[d] = d + forward_time_by
    grib.adjust_time(dates_map, args.currents_out_grib)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("--currents-src-grib", help="Original currents GRIB file", required=True)
    parser.add_argument("--currents-out-grib", help="Output currents GRIB file", required=True)
    parser.add_argument("--start-date-utc", help="GRIB UTC start date YYYY-MM-DD", required=True)
    parser.add_argument("--work-dir", help="Directory to keep clips", default='./data')
    params, unknown = parser.parse_known_args()
    make_const_wind_grib(params)

