import argparse

from grib import Grib


def make_constant_wind_grib(args):
    grib = Grib(args.template_grib)
    grib.force_wind(float(args.tws), float(args.twd), args.output_grib, args.start_date_utc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("--template-grib", help="Template GRIB file", required=True)
    parser.add_argument("--output-grib", help="Output GRIB file", required=True)
    parser.add_argument("--start-date-utc", help="GRIB UTC start date YYYY-MM-DD", required=True)
    parser.add_argument("--tws", help="Wind speed [kts]", required=True)
    parser.add_argument("--twd", help="Wind direction [degrees]", required=True)
    parser.add_argument("--work-dir", help="Directory to keep clips", default='./data')
    params = parser.parse_args()
    make_constant_wind_grib(params)

