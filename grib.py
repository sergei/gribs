import datetime
import io
import math
import os.path
import subprocess

WGRIB_BIN = os.path.expanduser('bin/osx/wgrib2')


class Grib:
    def __init__(self, grib_name):
        self.grib_name = grib_name
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
