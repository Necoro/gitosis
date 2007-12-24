from nose.tools import eq_ as eq, assert_raises, raises

from gitosis import sshkey

def test_sshkey_extract_user_simple():
    got = sshkey.extract_user(
            'ssh-somealgo '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fakeuser@fakehost')
    eq(got, 'fakeuser@fakehost')

def test_sshkey_extract_user_domain():
    got = sshkey.extract_user(
            'ssh-somealgo '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fakeuser@fakehost.example.com')
    eq(got, 'fakeuser@fakehost.example.com')

def test_sshkey_extract_user_domain_dashes():
    got = sshkey.extract_user(
            'ssh-somealgo '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fakeuser@ridiculously-long.example.com')
    eq(got, 'fakeuser@ridiculously-long.example.com')

def test_sshkey_extract_user_underscore():
    got = sshkey.extract_user(
            'ssh-somealgo '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fake_user@example.com')
    eq(got, 'fake_user@example.com')

def test_sshkey_extract_user_dot():
    got = sshkey.extract_user(
            'ssh-somealgo '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fake.u.ser@example.com')
    eq(got, 'fake.u.ser@example.com')

def test_sshkey_extract_user_dash():
    got = sshkey.extract_user(
            'ssh-somealgo '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fake.u-ser@example.com')
    eq(got, 'fake.u-ser@example.com')

def test_sshkey_extract_user_no_at():
    got = sshkey.extract_user(
            'ssh-somealgo '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fakeuser')
    eq(got, 'fakeuser')

def test_sshkey_extract_user_caps():
    got = sshkey.extract_user(
            'ssh-somealgo '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= Fake.User@Domain.Example.Com')
    eq(got, 'Fake.User@Domain.Example.Com')

@raises(sshkey.InsecureSSHKeyUsername)
def test_sshkey_extract_user_bad():
    try:
        sshkey.extract_user(
        'ssh-somealgo AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= ER3%#@e%')
    except sshkey.InsecureSSHKeyUsername, e:
        eq(str(e), "Username contains not allowed characters: 'ER3%#@e%'")
        raise e
