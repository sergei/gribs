import datetime
import io
import math
import os.path
import shutil
import subprocess

WGRIB_BIN = os.path.expanduser('bin/osx/wgrib2')
GRIB_GET_BIN = '/usr/local/bin/grib_get'
GRIB_SET_BIN = '/usr/local/bin/grib_set'


class Grib:
    def __init__(self, grib_name, work_dir=None):
        self.grib_name = grib_name
        self.work_dir = work_dir
        self.toc = None

    def read_grib_toc(self):
        cmd = [WGRIB_BIN, self.grib_name]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        result = process.communicate()[0].decode('utf-8')
        toc = {}
        for line in io.StringIO(result):
            t = line.split(':')
            time = datetime.datetime.strptime(t[2], 'd=%Y%m%d%H')
            if time not in toc:
                toc[time] = {}
            if t[3] == 'UGRD':
                toc[time]['u'] = int(t[0])
            if t[3] == 'VGRD':
                toc[time]['v'] = int(t[0])

        return toc

    def get_wind_from_grib(self, utc_time, lat, lon):
        if self.toc is None:
            self.toc = self.read_grib_toc()

        grib_time = datetime.datetime.combine(utc_time.date(), datetime.time(utc_time.hour, 0, 0))
        if grib_time not in self.toc:
            print(f'date {grib_time} is not part of the GRIB file')
            return None, None

        min_idx = min(self.toc[grib_time]['u'], self.toc[grib_time]['v'])

        cmd = [WGRIB_BIN, self.grib_name, '-for', f'{min_idx}:{min_idx+1}', '-lola', f'{lon + 360}:1:1', f'{lat}:1:1',
               '-', 'text']
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        result = process.communicate()[0].decode('utf-8')
        lines = io.StringIO(result).readlines()

        # Find if the first record is U or V
        if lines[2].split(':')[2] == 'UGRD':
            u_idx = 1
            v_idx = 4
        else:
            v_idx = 1
            u_idx = 4

        u = float(lines[u_idx].strip())
        v = float(lines[v_idx].strip())
        speed_ms = math.sqrt(u**2 + v**2)
        speed_kts = speed_ms * 3600 / 1852
        direction = math.degrees(math.atan2(v, u)) % 360
        return speed_kts, direction

    def force_wind(self, tws_kts, twd_deg, out_grib_name, start_date_utc):
        csv_file = 'data/out.csv'
        txt_file = 'data/in.txt'
        cmd = [WGRIB_BIN, self.grib_name,  '-no_header', '-csv', csv_file]
        tws_ms = tws_kts * 1852 / 3600
        twd_rad = math.radians(twd_deg + 180)
        u = tws_ms * math.sin(twd_rad)
        v = tws_ms * math.cos(twd_rad)

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        process.communicate()[0].decode('utf-8')

        with open(csv_file, 'r') as f_cvs, open(txt_file, 'w') as f_txt:
            for line in f_cvs:
                t = line.split(',')
                if t[2] == '"UGRD"':
                    f_txt.write(f'{u}\n')
                if t[2] == '"VGRD"':
                    f_txt.write(f'{v}\n')

        t = start_date_utc.split('-')
        d = t[0] + t[1] + t[2]  + '00'
        print(f'Writing {out_grib_name}')
        cmd = [WGRIB_BIN, self.grib_name, '-no_header',
               '-set_date', d,
               '-import_text', txt_file, '-grib_out', out_grib_name]
        print(f'Running {" ".join(cmd)}')

        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        result = process.communicate()[0].decode('utf-8')
        io.StringIO(result).readlines()

    def adjust_time(self, dates_map,  new_grib_name):
        # Read current time stamps from the GRIB file

        input_grib_name = self.grib_name
        count = 0
        tmp_grib_name = None
        for orig_date in dates_map:
            tmp_grib_name = self.work_dir + os.sep + f'tmp{count}.grib'
            new_date = dates_map[orig_date]
            cmd = [GRIB_SET_BIN,
                   '-s', f'dataDate={new_date.strftime("%Y%m%d")},dataTime={new_date.strftime("%H%M")}',
                   '-w', f'dataDate={orig_date.strftime("%Y%m%d")},dataTime={orig_date.strftime("%H%M")}',
                   input_grib_name, tmp_grib_name]
            print(f'Running {" ".join(cmd)}')
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            result = process.communicate()[0].decode('utf-8')
            for line in io.StringIO(result):
                print(line)
            count += 1
            input_grib_name = tmp_grib_name

        if tmp_grib_name is not None:
            shutil.copyfile(tmp_grib_name, new_grib_name)

    def get_dates(self):
        # Read current time stamps from the GRIB file

        cmd = [GRIB_GET_BIN, '-p', 'dataDate,dataTime', self.grib_name]
        print(f'Running {" ".join(cmd)}')
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        result = process.communicate()[0].decode('utf-8')
        dates = []
        for line in io.StringIO(result):
            t = line.split()
            d = datetime.datetime.strptime(t[0] + t[1], '%Y%m%d%H')
            dates.append(d)

        return dates
