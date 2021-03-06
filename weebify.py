import argparse
import enzyme
import sys
import subprocess

SUBTITLES_AVOID_TEXT = ['lyrics', 'signs']


def should_avoid_default_sub(mkv):
    return len(mkv.subtitle_tracks) > 1 and \
           any([any([avoid in s.name.lower() for avoid in SUBTITLES_AVOID_TEXT]) for s in mkv.subtitle_tracks if s.default and s.name])


def find_eng_sub(mkv):
    return [s for s in mkv.subtitle_tracks if all([avoid not in s.name.lower() for avoid in SUBTITLES_AVOID_TEXT])][0]


def weebify_mkv(mkv_path, noop=False):
    print('Opening {}'.format(mkv_path), file=sys.stderr)
    with open(mkv_path, 'rb') as fp:
        mkv = enzyme.MKV(fp)

    jpn_audio_track = find_jpn_audio_track(mkv)
    def_audio_track = find_default_audio_track(mkv)
    set_default_sub = should_avoid_default_sub(mkv)
    set_default_audio = jpn_audio_track and jpn_audio_track != def_audio_track
    track_changes = {track.number: [] for track in mkv.audio_tracks + mkv.subtitle_tracks}
    if set_default_audio:
        if noop:
            print('Would flag audio track {} as default'.format(jpn_audio_track.number), file=sys.stderr)
        track_changes[jpn_audio_track.number].append('flag-default=1')
        for track in mkv.audio_tracks:
            if track != jpn_audio_track and track.default:
                if noop:
                    print('Would unflag audio track {} as default'.format(track.number), file=sys.stderr)
                track_changes[track.number].append('flag-default=0')
    if set_default_sub:
        primary_eng_sub = find_eng_sub(mkv)
        if noop:
            print('Would flag subtitle track {} as default'.format(primary_eng_sub.number), file=sys.stderr)
        track_changes[primary_eng_sub.number].append('flag-default=1')
        for track in mkv.subtitle_tracks:
            if track != primary_eng_sub and track.default:
                if noop:
                    print('Would unflag subtitle track {} as default'.format(track.number), file=sys.stderr)
                track_changes[track.number].append('flag-default=0')

    args = build_args(track_changes)
    if args:
        if noop:
            return 1
        else:
            subprocess.check_call(['mkvpropedit', '-v', mkv_path, '-v'] + args)
            return 0
    else:
        print('Nothing to do', file=sys.stderr)
        return 0


def build_args(track_changes):
    args = []
    for track_number, changes in [(k, v) for k, v in track_changes.items() if v]:
        args.extend(['--edit', 'track:{}'.format(track_number)])
        for change in changes:
            args.extend(['--set', change])
    return args


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
    return weebify_mkv(args.input_file, args.noop)

if __name__ == '__main__':
    exit(main())
