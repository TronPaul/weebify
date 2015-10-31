import argparse
import enzyme
import sys
import subprocess


def webify_mkv(mkv_path):
    with open(mkv_path, 'rb') as fp:
        mkv = enzyme.MKV(fp)

    jpn_track = find_jpn_audio_track(mkv)
    def_track = find_default_audio_track(mkv)
    set_default = jpn_track != def_track
    args = ['mkvpropedit', '-v', mkv_path, '-v', '--edit', 'track:{}'.format(jpn_track.number)]
    if set_default:
        args.extend(['--set', 'flag-default=1'])
        for track in mkv.audio_tracks:
            if track != jpn_track:
                if set_default and track.default:
                    args.extend(['--edit', 'track:{}'.format(track.number), '--set', 'flag-default=0'])
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
