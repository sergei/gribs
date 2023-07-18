import argparse
import glob
import os

import gpxpy
import gpxpy.gpx

from grib import Grib


def wind_stat(args):
    time_slots = {}
    with open(args.gpx_file, 'r') as gpx_file, open(args.csv_file, 'wt') as out_csv:
        gpx = gpxpy.parse(gpx_file)

        # Read list of GRIB files from args.grib_dir
        grib_files = glob.glob(args.grib_dir + '/*.grib2')
        out_csv.write(f'UTC')
        for grib_file in grib_files:
            name = os.path.basename(grib_file).split('.')[0]
            out_csv.write(f',{name}')
            grib = Grib(grib_file)

            for route in gpx.routes:
                print('Route:')
                for point in route.points:
                    aws, awd = grib.get_wind_from_grib(point.time, point.latitude, point.longitude)
                    if point.time not in time_slots:
                        time_slots[point.time] = {'aws': [], 'awd': []}
                    time_slots[point.time]['aws'].append(aws)
                    time_slots[point.time]['awd'].append(awd)

        out_csv.write(f'\n')
        for t in sorted(time_slots.keys()):
            out_csv.write(f'{t}')
            for aws in time_slots[t]["aws"]:
                if aws is None:
                    out_csv.write(',')
                else:
                    out_csv.write(f',{aws:.1f}')
            out_csv.write(f'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("--grib-dir", help="Directory containing GRIB files", required=True)
    parser.add_argument("--gpx-file", help="GPX file containing the route", required=True)
    parser.add_argument("--csv-file", help="CSV file containing the wind stats", required=True)
    wind_stat(parser.parse_args())
