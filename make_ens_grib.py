""" This script merges multiple highway GRIB files to the single one """
import argparse
import glob
import os
import subprocess
import tempfile

from grib import WGRIB_BIN

# See https://www.nco.ncep.noaa.gov/pmb/docs/grib2/grib2_doc/grib2_table4-0.shtml
ENS_MEM_TYPE = 3


def make_ensemble_grib(highway_dir, ens_grib):
    with tempfile.TemporaryDirectory() as work_dir:
        print('created temporary directory', work_dir)
        grib_files = glob.glob(highway_dir + '/*.grib2')
        num_of_forecasts = len(grib_files)
        ens_gribs = []
        for num, grib_file in enumerate(sorted(grib_files)):
            pert_num = num + 1
            out_grib_name = os.path.join(work_dir, f'ens_{pert_num:02d}.grib2')
            cmd = [WGRIB_BIN, '-set_ens_num', f'{ENS_MEM_TYPE}', f'{pert_num}', f'{num_of_forecasts}', f'{grib_file}',
                   '-grib', out_grib_name]
            print(f'Running {" ".join(cmd)}')
            subprocess.run(cmd)
            ens_gribs += [out_grib_name]

        with open(ens_grib, 'wb') as ens_file:
            for grib in ens_gribs:
                if os.path.isfile(grib):
                    print(f' Appending {grib} to {ens_grib}')
                    with open(grib, 'rb') as f:
                        ens_file.write(f.read())
                    os.unlink(grib)
                else:
                    print(f' {grib} does not exist')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("--work-dir", help="Directory to keep GRIB files", default='./data')
    parser.add_argument("--highway-dir", help="Directory containing highway GRIBs", required=True)
    parser.add_argument("--ens-grib", help="Ensemble grib", required=True)
    args = parser.parse_args()
    make_ensemble_grib(args.highway_dir, args.ens_grib)


