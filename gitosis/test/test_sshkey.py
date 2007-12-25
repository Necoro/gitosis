from nose.tools import eq_ as eq, assert_raises, raises

from gitosis import sshkey

def test_sshkey_username_simple():
    _ = sshkey.get_ssh_pubkey(
            'ssh-rsa '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fakeuser@fakehost')
    got = _.username
    eq(got, 'fakeuser@fakehost')

def test_sshkey_username_domain():
    _ = sshkey.get_ssh_pubkey(
            'ssh-rsa '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fakeuser@fakehost.example.com')
    got = _.username
    eq(got, 'fakeuser@fakehost.example.com')

def test_sshkey_username_domain_dashes():
    _ = sshkey.get_ssh_pubkey(
            'ssh-rsa '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= '
            +'fakeuser@ridiculously-long.example.com')
    got = _.username
    eq(got, 'fakeuser@ridiculously-long.example.com')

def test_sshkey_username_underscore():
    _ = sshkey.get_ssh_pubkey(
            'ssh-rsa '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fake_user@example.com')
    got = _.username
    eq(got, 'fake_user@example.com')

def test_sshkey_username_dot():
    _ = sshkey.get_ssh_pubkey(
            'ssh-rsa '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fake.u.ser@example.com')
    got = _.username
    eq(got, 'fake.u.ser@example.com')

def test_sshkey_username_dash():
    _ = sshkey.get_ssh_pubkey(
            'ssh-rsa '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fake.u-ser@example.com')
    got = _.username
    eq(got, 'fake.u-ser@example.com')

def test_sshkey_username_no_at():
    _ = sshkey.get_ssh_pubkey(
            'ssh-rsa '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= fakeuser')
    got = _.username
    eq(got, 'fakeuser')

def test_sshkey_username_caps():
    _ = sshkey.get_ssh_pubkey(
            'ssh-rsa '
            +'0123456789ABCDEFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
            +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= Fake.User@Domain.Example.Com')
    got = _.username
    eq(got, 'Fake.User@Domain.Example.Com')

@raises(sshkey.InsecureSSHKeyUsername)
def test_sshkey_username_bad():
    # The '#' and characters after it are part of an actual comment in the file
    # and are ignored.
    try:
        _ = sshkey.get_ssh_pubkey(
        'ssh-rsa AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
        +'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA= ER3%#@e%')
        got = _.username
    except sshkey.InsecureSSHKeyUsername, e:
        eq(str(e), "Username contains not allowed characters: 'ER3%'")
        raise e
