import argparse
import csv
import datetime

from grib import Grib


def verify_model(args):
    grib = Grib(args.grib_file)

    with open(args.csv_file, 'r') as csv_file, open(args.out_csv, 'wt') as out_csv:
        csv_reader = csv.DictReader(csv_file, delimiter=',', quotechar='|')
        writer = csv.DictWriter(out_csv, fieldnames=['utc', 'tws', 'gws', 'twd', 'gwd'])
        writer.writeheader()
        prev_utc_time = None
        for row in csv_reader:
            local_time = datetime.datetime.strptime(row['Date'] + ' ' + row['LocalTime'], '%d:%m:%Y %H:%M:%S.%f')
            utc_time = local_time - datetime.timedelta(hours=int(row['Zone']))
            if prev_utc_time is None:
                prev_utc_time = utc_time
            if (utc_time - prev_utc_time).total_seconds() >= args.step_minutes * 60:
                prev_utc_time = utc_time
                lat = float(row['Lat'])
                lon = float(row['Lon'])
                tws = float(row['yTWS'])
                twa = float(row['yTWA'])
                sow = float(row['ySpeed'])
                sog = float(row['ySOG'])
                cog = float(row['yCOG']) if len(row['yCOG']) > 0 else None

                if cog is not None:
                    twd = (cog + twa) % 360
                    print(f'{utc_time} {tws} {twd} {lat} {lon}')
                    gws, gwd = grib.get_wind_from_grib(utc_time, lat, lon)
                    writer.writerow({'utc': utc_time, 'tws': tws, 'gws': gws, 'twd': twd, 'gwd': gwd})


if __name__ == '__main__':
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("--grib-file", help="GRIB file", required=True)
    parser.add_argument("--csv-file", help="CSV file containing the boat data", required=True)
    parser.add_argument("--out-csv", help="CSV file containing the comparison", required=True)
    parser.add_argument("--step-minutes", help="CSV file containing the boat data", required=False,
                        type=int, default=1)
    verify_model(parser.parse_args())
