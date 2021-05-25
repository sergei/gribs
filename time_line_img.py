import argparse
import datetime
from moviepy.editor import *

from PIL import Image, ImageDraw, ImageFont


def make_time_line(args):
    print(f'Reading tide clip {args.input_clip} ...')
    tide_clip = VideoFileClip(args.input_clip)
    frames_num = len(list(tide_clip.iter_frames()))
    # frames_num = 2
    start_time = datetime.datetime.strptime(args.start_time, '%Y-%m-%d %H:%M')
    tidal_cycle_sec = (25 * 60 + 30) * 60
    dt = tidal_cycle_sec / frames_num

    fnt = ImageFont.truetype('/Library/Fonts/Arial.ttf', 84)
    file_list = []
    print(f'Creating time line clip')
    for i in range(frames_num):
        time = start_time + datetime.timedelta(seconds=i * dt)
        str_time = time.strftime("%m/%d/%Y %H:%M:%S")
        print('.', end='')

        filename = args.work_dir + os.sep + f'timeline-{i:03d}.png'
        img = Image.new('RGBA', (800, 80), (0, 255, 255, 0))
        d = ImageDraw.Draw(img)
        d.text((0, 0), str_time, font=fnt,  fill=(255, 255, 0))

        img.save(filename)
        file_list.append(filename)

    print('')
    time_line = ImageSequenceClip(file_list, fps=tide_clip.fps)
    # Position te time line
    x = tide_clip.w/2 - time_line.w/2
    y = time_line.h/2
    print(f'Creating composed clip')
    full_video = CompositeVideoClip([tide_clip, time_line.set_position((x, y))])
    race_video = full_video.subclip(5, 12)
    slow_race_video = race_video.fx(vfx.speedx, 0.5)

    print(f'Storing {args.output_clip} ...')
    slow_race_video.write_videofile(args.output_clip)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    parser.add_argument("--input-clip", help="Input clip", required=True)
    parser.add_argument("--output-clip", help="Output clip", required=True)
    parser.add_argument("--start-time", help="Slack before the max ebb time YYYY-MM-DD HH:MM", required=True)
    parser.add_argument("--work-dir", help="Directory to keep clips", default='./data/movie')
    params = parser.parse_args()
    make_time_line(params)
