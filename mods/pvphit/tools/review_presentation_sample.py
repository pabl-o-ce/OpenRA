"""Capture the sample in a private map with actual OpenAL wave output.

No playable map, shared settings, account or result endpoint is changed.
Use a fresh --tag for every run; review captures are never silently replaced.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

MOD = Path(__file__).resolve().parents[1]
ROOT = MOD.parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--display', default=':117')
    parser.add_argument('--size', default='1280,1000')
    parser.add_argument('--scale', type=float, default=1)
    parser.add_argument('--scenario', choices=('sample', 'hidden', 'visible', 'fog', 'muted'), default='sample')
    parser.add_argument('--seconds', type=int, default=120, help='Wall-clock timeout; completion follows simulation markers')
    args = parser.parse_args()
    if not args.tag.replace('-', '').isalnum():
        parser.error('Use a simple alphanumeric tag')
    width, height = map(int, args.size.split(','))
    if args.scale not in (1, 1.25, 1.5, 1.75, 2) or width / args.scale < 1024 or height / args.scale < 720:
        parser.error('Unsupported effective UI size')
    work = MOD / '.work' / ('presentation-' + args.tag)
    work.mkdir()  # A previous capture is evidence; never overwrite it.
    support = work / 'support'
    path = support / 'maps/pvphit/{DEV_VERSION}/presentation-review'
    path.mkdir(parents=True)
    (support / 'Content').symlink_to(MOD / '.work/support/Content')
    shutil.copyfile(MOD / 'maps/foundry-environment-checks/map.bin', path / 'map.bin')
    text = (MOD / 'maps/foundry-environment-checks/map.yaml').read_text().replace('checks.lua', 'review.lua')
    text = text.replace('FogCheckboxEnabled: false', 'FogCheckboxEnabled: true')
    text = text.replace('ExploredMapCheckboxEnabled: true', 'ExploredMapCheckboxEnabled: ' + ('true' if args.scenario == 'fog' else 'false'))
    (path / 'map.yaml').write_text(text)
    lua = (MOD / 'tools/presentation_sample.lua').read_text().replace('SCENARIO', args.scenario)
    (path / 'review.lua').write_text(lua)
    muted = args.scenario == 'muted'
    (support / 'settings.yaml').write_text(
        'Player:\n\tName: Presentation-Review\nGame:\n\tViewportEdgeScroll: False\n\tMouseScroll: Disabled\n'
        f'Sound:\n\tMusicVolume: 0\n\tMute: {str(muted).lower()}\n'
        f'Graphics:\n\tMode: Windowed\n\tVSync: False\n\tWindowedSize: {args.size}\n\tUIScale: {args.scale}\n'
        '\tViewportDistance: Native\nServer:\n\tAdvertiseOnline: False\n')
    config = work / 'alsoft.conf'
    config.write_text('[general]\nchannels = stereo\nsample-type = int16\nfrequency = 44100\n'
                      '[wave]\nfile = ' + str(work / 'engine.wav') + '\n')
    env = dict(os.environ, DISPLAY=args.display, LIBGL_ALWAYS_SOFTWARE='1', ALSOFT_DRIVERS='wave',
               ALSOFT_CONF=str(config), SDL_VIDEODRIVER='x11', LP_NUM_THREADS='2')
    env.pop('PVPHIT_MATCH_ID', None)
    processes, handles = [], []
    def launch(command, log):
        handle = open(work / log, 'w')
        handles.append(handle)
        p = subprocess.Popen(command, cwd=ROOT, env=env, stdout=handle, stderr=subprocess.STDOUT)
        processes.append(p)
        return p
    try:
        socket = Path('/tmp/.X11-unix/X' + args.display[1:])
        if socket.exists():
            raise RuntimeError('Display occupied; select an unused display')
        display = launch(['Xvfb', args.display, '-screen', '0', f'{width}x{height}x24', '-nolisten', 'tcp'], 'display.log')
        for _ in range(50):
            if display.poll() is not None:
                raise RuntimeError('Xvfb failed: ' + (work / 'display.log').read_text())
            if socket.exists():
                break
            time.sleep(.1)
        game = launch([str(MOD / '.work/dotnet/dotnet'), 'bin/OpenRA.dll', 'Engine.EngineDir=' + str(ROOT),
                       'Engine.SupportDir=' + str(support), 'Game.Mod=pvphit', 'Launch.Map=presentation-review',
                       'Graphics.CapFramerate=True', 'Graphics.MaxFramerate=30'], 'game.log')
        launch(['ffmpeg', '-nostdin', '-loglevel', 'error', '-f', 'x11grab', '-framerate', '15',
                '-video_size', f'{width}x{height}', '-i', args.display, '-t', str(args.seconds + 15),
                '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '22', str(work / 'video.mkv')], 'video.log')
        start = time.monotonic()
        ready = None
        complete = False
        captures, events, seen = [], [], set()
        while time.monotonic() - start < args.seconds:
            log = (work / 'game.log').read_text()
            if game.poll() is not None or any(s in log for s in ('Fatal Lua Error', 'Exception', 'FAILED')):
                raise RuntimeError(log[-4000:])
            if 'PRESENTATION READY' in log and ready is None:
                ready = time.monotonic()
            for line in log.splitlines():
                line = line.removeprefix('Lua debug: ')
                if line.startswith('PRESENTATION') and line not in seen:
                    seen.add(line)
                    events.append({'wall_seconds': round(time.monotonic() - start, 3), 'event': line})
                    print(line, flush=True)
                    if line == 'PRESENTATION INPUT select':
                        commands = [f'move,{width//2-12},{height//2-15}', 'click,1']
                    elif line == 'PRESENTATION INPUT move':
                        commands = [f'move,{width//2+36},{height//2}', 'click,3']
                    elif line == 'PRESENTATION INPUT attack':
                        commands = [f'move,{width//2+120},{height//2-5}', 'down,Control_L', 'click,3', 'up,Control_L']
                    elif line == 'PRESENTATION CAPTURE warning':
                        subprocess.run(['magick', 'import', '-window', 'root', str(work / 'warning.png')], env=env, check=True)
                        continue
                    elif line == 'PRESENTATION COMPLETE':
                        complete = True
                        continue
                    else:
                        continue
                    subprocess.run(['python3', str(MOD / 'tools/yard_input.py'), *commands], env=env, check=True, stdout=subprocess.DEVNULL)
            if ready is not None:
                elapsed = time.monotonic() - ready
                for second in (4, 13, 17, 23, 35):
                    if elapsed >= second and second not in captures:
                        if second == 13:
                            # Hover the resource/power counter using logical UI coordinates.
                            x = width - round(70 * args.scale)
                            y = round(284 * args.scale)
                            subprocess.run(['python3', str(MOD / 'tools/yard_input.py'), f'move,{x},{y}', 'wait,0.7'], env=env, check=True, stdout=subprocess.DEVNULL)
                        subprocess.run(['magick', 'import', '-window', 'root', str(work / f'{second}.png')], env=env, check=True)
                        captures.append(second)
                if complete:
                    break
            time.sleep(.15)
        if ready is None or not complete:
            raise RuntimeError('Game did not finish the scenario before timeout')
        (work / 'events.json').write_text(json.dumps(events, indent=2) + '\n')
        (work / 'capture.json').write_text(json.dumps(vars(args), indent=2) + '\n')
    finally:
        for process in reversed(processes):
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        for handle in handles:
            handle.close()
    # Termination may leave RIFF sizes unset: ffmpeg reads to EOF and finalizes a review WAV.
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(work / 'engine.wav'),
                    '-c:a', 'pcm_s16le', str(work / 'review.wav')], check=True)
    subprocess.run(['ffmpeg', '-nostdin', '-v', 'error', '-i', str(work / 'video.mkv'), '-i', str(work / 'review.wav'),
                    '-c:v', 'copy', '-c:a', 'aac', '-shortest', str(work / 'review.mp4')], check=True)
    print(work, flush=True)


if __name__ == '__main__':
    main()
