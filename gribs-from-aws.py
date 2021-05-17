import argparse
import datetime
import io
import os.path
import shutil
import subprocess

import boto3 as boto3
from botocore import UNSIGNED
from botocore.config import Config

BUCKET_NAME = 'noaa-hrrr-bdp-pds'
WGRIB_BIN = os.path.expanduser('~/src/grib2/wgrib2/wgrib2')


def download_gribs(work_dir, start_date, hours_num, historical):
    s3 = boto3.client('s3', config=Config(signature_version=UNSIGNED))
    height_filter = ['10 m above ground']
    type_filter = ['UGRD', 'VGRD']
    small_grib_list = []
    if historical:
        fcst_hour = 0
        for i in range(hours_num):
            run_time = start_date + datetime.timedelta(hours=i)
            grib_name = f'hrrr.{run_time.year:04d}{run_time.month:02d}{run_time.day:02d}/conus' \
                f'/hrrr.t{run_time.hour:02d}z.wrfsfcf{fcst_hour:02d}.grib2'
            print(f'run_time = {run_time} grib_name = {grib_name}')

            # Download GRIB index file
            grib_idx_name = grib_name + '.idx'
            resp = s3.get_object(Bucket=BUCKET_NAME, Key=grib_idx_name)
            grib_index = resp['Body'].read().decode("utf-8")

            # Parse index file
            records = parse_grib_index(grib_index)

            # Download desired records of GRIB file
            local_grib_name = os.path.expanduser(work_dir + os.sep + grib_name.replace('/', '_'))
            with open(local_grib_name, 'wb') as gf:
                for record in records:
                    if record['height'] in height_filter and record['type'] in type_filter:
                        start_byte = record["start"]
                        stop_byte = record["end"]
                        print(f'Downloading range {start_byte} {stop_byte} from s3://{BUCKET_NAME}/{grib_name} ...')
                        resp = s3.get_object(Bucket=BUCKET_NAME, Key=grib_name, Range='bytes={}-{}'.format(start_byte,
                                                                                                           stop_byte))
                        res = resp['Body'].read()
                        gf.write(res)
                print(f'{local_grib_name} created.')

                t = local_grib_name.split('.')
                small_local_grib_name = '.'.join(t[0:-1]) + '.small.' + t[-1]
                print(f'Extract small grib to {small_local_grib_name}')

                args = [WGRIB_BIN, local_grib_name, '-small_grib', '-123:-122', '36:38', small_local_grib_name]
                subprocess.run(args)
                small_grib_list.append(small_local_grib_name)

        out_grib_name = work_dir + os.sep + f'hrrr-{start_date.year:04d}{start_date.month:02d}{start_date.day:02d}' \
                                            f'-{hours_num}hrs.small.grib2'
        print(f'Combine small gribs to one {out_grib_name} ...')
        with open(out_grib_name, 'wb') as out_grib:
            for small_grib in small_grib_list:
                in_grib = open(small_grib, 'rb')
                shutil.copyfileobj(in_grib, out_grib)
                in_grib.close()
            print(f'{out_grib_name} created.')
    else:
        print('Not supported yet')


def decode_record(t):
    return {
        'start': int(t[1]),
        'type': t[3],
        'height': t[4]
    }


def parse_grib_index(grib_index):
    records = []
    for line in io.StringIO(grib_index):
        t = line.split(':')
        records.append(decode_record(t))
    # Add the end of record information
    for i in range(0, len(records) - 1):
        records[i]['end'] = records[i + 1]['start'] - 1
    return records


def gribs_from_aws(args):
    if args.historical is not None:
        start_date = datetime.datetime.strptime(args.start_date, '%Y-%m-%d')
    else:
        start_date = datetime.date.today()

    start_date = start_date + datetime.timedelta(hours=args.start_hour)
    print(f'Starting date {start_date}')

    download_gribs(args.work_dir, start_date, args.hours_num, args.historical)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("--work-dir", help="Directory to keep GRIB files", default='./data')
    parser.add_argument("--start-date", help="Starting date YYYY-MM-DD", required=False)
    parser.add_argument("--start-hour", help="Starting hour HH", required=False, type=int,  default=0)
    parser.add_argument("--hours-num", help="Number of hours", required=False, type=int, default=24)
    parser.add_argument("--historical", help="Get historical winds using F0 only", required=False, action='store_true')
    gribs_from_aws(parser.parse_args())
