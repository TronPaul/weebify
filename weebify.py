import argparse
import enzyme
import sys
import subprocess


def webify_mkv(mkv_path):
    with open(mkv_path, 'rb') as fp:
        mkv = enzyme.MKV(fp)

    first_track = mkv.audio_tracks[0]
    jpn_track = find_jpn_audio_track(mkv)
    def_track = find_default_audio_track(mkv)
    set_default = jpn_track != def_track
    change_order = jpn_track != first_track
    args = ['mkvpropedit', '-v', mkv_path, '-v', '--edit', 'track:{}'.format(jpn_track.number)]
    if change_order:
        args.extend(['--set', 'track-number={}'.format(first_track.number)])
    if set_default:
        args.extend(['--set', 'flag-default=1'])

    if change_order or set_default:
        next_track_index = 0
        for track in mkv.audio_tracks:
            if track != jpn_track:
                additional_args = ['--edit', 'track:{}'.format(track.number)]
                extend = False
                if change_order and next_track_index != track.number:
                    additional_args.extend(['--set', 'track-number={}'.format(mkv.audio_tracks[next_track_index+1].number)])
                    extend = True
                if set_default and track.default:
                    additional_args.extend(['--set', 'flag-default=0'])
                    extend = True
                if extend:
                    args.extend(additional_args)
                next_track_index += 1
    if change_order or set_default:
        subprocess.check_call(args)
    else:
        print("Nothing to do", file=sys.stderr)


def find_jpn_audio_track(mkv):
    for audio_track in mkv.audio_tracks:
        if audio_track.language == 'jpn':
            return audio_track


def find_default_audio_track(mkv):
    for audio_track in mkv.audio_tracks:
        if audio_track.default:
            return audio_track

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--noop", action='store_true')
    parser.add_argument("input_file")

    args = parser.parse_args()
    webify_mkv(args.input_file)

if __name__ == '__main__':
    main()
