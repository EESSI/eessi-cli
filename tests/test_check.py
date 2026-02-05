import eessi.cli.check
from eessi.cli.check import UNKNOWN, get_repo_attribute


def test_get_repo_attribute(monkeypatch):
    """
    Tests for get_repo_attribute
    """

    out = '\n'.join([
        'Attribute "revision" had a 5 byte value for /cvmfs/software.eessi.io:',
        '13972',
    ])
    monkeypatch.setattr(eessi.cli.check, 'run_cmd', lambda x: (out, '', 0))
    res = get_repo_attribute('software.eessi.io', 'revision')
    assert res == '13972'

    # check that UNKNOWN is returned when attr returns '0 byte value' with empty last line
    out = '\n'.join([
        'Attribute "ncleanup24" had a 0 byte value for /cvmfs/software.eessi.io:',
        '',
    ])
    monkeypatch.setattr(eessi.cli.check, 'run_cmd', lambda x: (out, '', 0))
    res = get_repo_attribute('software.eessi.io', 'ncleanup24')
    assert res == UNKNOWN
