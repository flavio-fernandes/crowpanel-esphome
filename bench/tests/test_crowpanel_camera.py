"""CrowPanel presentation stays stable while transport uses fake SSH only."""
from pathlib import Path

import pytest

from test_client_tools import client  # noqa: F401


def test_sequence_defaults_and_intervals(client):
    run, calls, tmp = client
    sleeper = tmp / 'bin/sleep'
    sleeper.write_text('#!/bin/sh\nprintf "%s\\n" "$1" >> "${CALLS}.sleeps"\n')
    sleeper.chmod(0o755)
    result = run('crowpanel-camera-sequence', settings={'OUTPUT_HEX': 'abcd'})
    assert result.returncode == 0, result.stderr
    paths = result.stdout.decode().splitlines()
    assert len(paths) == 4
    assert len({str(Path(p).parent) for p in paths}) == 1
    assert paths[0].startswith('artifacts/crowpanel-camera-')
    assert [Path(p).name for p in paths] == [f'frame-{i:02}.jpg' for i in range(1, 5)]
    assert (tmp / 'calls.sleeps').read_text().splitlines() == ['3'] * 3
    assert calls() == [['bench-agent', 'snap']] * 4
    assert all((tmp / p).read_bytes() == bytes.fromhex('abcd') for p in paths)


@pytest.mark.parametrize('args', [('0',), ('61',), ('1', '601'), ('1', '-1'),
                                       ('1', '1', 'extra'), ('999999999999',), ('a',)])
def test_bad_sequence_does_not_connect(client, args):
    run, calls, tmp = client
    assert run('crowpanel-camera-sequence', *args).returncode == 2
    assert calls() == []
    assert not (tmp / 'artifacts').exists()


def test_capture_failure_preserves_photo_and_stops_sequence(client):
    run, calls, tmp = client
    photo = tmp / 'existing.jpg'
    photo.write_bytes(b'previous photo')
    result = run('crowpanel-camera-capture', photo,
                 settings={'SSH_RC': '65', 'OUTPUT_HEX': 'abcd'})
    assert result.returncode == 65
    assert photo.read_bytes() == b'previous photo'
    assert not list(tmp.glob('*.part.*'))
    result = run('crowpanel-camera-sequence', '4', '0', settings={'SSH_RC': '66'})
    assert result.returncode == 66
    assert result.stdout == b''
    assert len(calls()) == 2
    assert not list((tmp / 'artifacts').rglob('*.jpg'))
    assert not list((tmp / 'artifacts').rglob('*.part.*'))


def test_camera_legacy_config_precedence(client):
    run, calls, tmp = client
    config = tmp / 'camera.env'
    config.write_text('BENCH_CAMERA_WIDTH=640\nBENCH_CAMERA_HEIGHT=480\n'
                      'CROWPANEL_CAMERA_WIDTH=1280\nCROWPANEL_CAMERA_SKIP=10\n')
    result = run('crowpanel-camera-capture', tmp / 'photo.jpg', settings={
        'BENCH_CONFIG_FILE': str(config), 'CROWPANEL_CAMERA_WIDTH': '320',
        'CROWPANEL_CAMERA_DEVICE': '/dev/not-a-client-camera'})
    assert result.returncode == 0, result.stderr
    assert calls()[-1] == ['bench-agent', 'snap', 'res=320x480', 'skip=10']
    assert b'CROWPANEL_CAMERA_DEVICE is retired and ignored' in result.stderr
    result = run('crowpanel-camera-capture', tmp / 'photo.jpg', settings={
        'BENCH_CONFIG_FILE': str(config), 'CROWPANEL_CAMERA_WIDTH': '320',
        'BENCH_CAMERA_WIDTH': '800', 'BENCH_CAMERA_SKIP': '2'})
    assert result.returncode == 0
    assert calls()[-1] == ['bench-agent', 'snap', 'res=800x480', 'skip=2']


def test_capture_default_path_and_help(client):
    run, calls, tmp = client
    for tool in ('crowpanel-camera-capture', 'crowpanel-camera-sequence'):
        assert run(tool, '--help').returncode == 0
    assert calls() == []
    result = run('crowpanel-camera-capture', settings={'OUTPUT_HEX': 'abcd'})
    assert result.returncode == 0
    path = result.stdout.decode().strip()
    assert path.startswith('artifacts/crowpanel-camera-') and path.endswith('.jpg')
    assert (tmp / path).read_bytes() == bytes.fromhex('abcd')
    assert (tmp / path).stat().st_mode & 0o777 == 0o600
