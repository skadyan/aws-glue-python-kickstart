from osiris.base.generalutils import flag


def test_flag_values():
    assert not flag(None)
    assert not flag('None')
    assert not flag('none')
    assert not flag('null')
    assert not flag('0')
    assert not flag(0)
    assert not flag('N')
    assert not flag('no')
    assert not flag('false')

    assert flag('true')
    assert flag(True)
    assert flag('Y')
