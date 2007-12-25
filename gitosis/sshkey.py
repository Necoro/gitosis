"""
Gitosis code to intelligently handle SSH public keys.

"""
from shlex import shlex
from StringIO import StringIO
import re

# The 'ecc' and 'ecdh' types are speculative, based on the Internet Draft
# http://www.ietf.org/internet-drafts/draft-green-secsh-ecc-02.txt
SSH_KEY_PROTO2_TYPES = ['ssh-dsa', 
                        'ssh-dss',
                        'ssh-ecc', 
                        'ssh-ecdh',
                        'ssh-rsa']

# These options must not have arguments
SSH_KEY_OPTS = ['no-agent-forwarding', 
                'no-port-forwarding', 
                'no-pty',
                'no-X11-forwarding']
# These options require arguments
SSH_KEY_OPTS_WITH_ARGS = ['command', 
                          'environment', 
                          'from', 
                          'permitopen', 
                          'tunnel' ]

class MalformedSSHKey(Exception):
    """Malformed SSH public key"""

class InsecureSSHKeyUsername(Exception):
    """Username contains not allowed characters"""
    def __str__(self):
        return '%s: %s' % (self.__doc__, ': '.join(self.args))

class SSHPublicKey:
    """Base class for representing an SSH public key"""
    def __init__(self, opts, keydata, comment):
        """Create a new instance."""
        self._options = opts
        self._comment = comment
        self._username = comment
        _ = comment.split(None)
        if len(_) > 1:
            self._username = _[0]
        _ = keydata

    @property
    def options(self):
        """Returns a dictionary of options used with the SSH public key."""
        return self._options

    @property
    def comment(self):
        """Returns the comment associated with the SSH public key."""
        return self._comment

    @property
    def username(self):
        """
        Returns the username from the comment, the first word of the comment.
        """
        if isSafeUsername(self._username):
            return self._username
        else:
            raise InsecureSSHKeyUsername(repr(self._username))
    
    def options_string(self):
        """Return the options array as a suitable string."""
        def _single_option():
            """Convert a single option to a usable string."""
            for (key, val) in self._options.items():
                _ = key
                if val is not None:
                    _ += "=\"%s\"" % (val.replace('"', '\\"'), )
                yield _
        return ','.join(_single_option())

    @property
    def key(self):
        """Abstract method"""
        raise NotImplementedError()

    @property
    def full_key(self):
        """Return a full SSH public key line, as found in authorized_keys"""
        options = self.options_string()
        if len(options) > 0:
            options += ' '
        return '%s%s %s' % (options, self.key, self.comment)

    def __str__(self):
        return self.full_key

class SSH1PublicKey(SSHPublicKey):
    """Class for representing an SSH public key, protocol version 1"""
    def __init__(self, opts, keydata, comment):
        """Create a new instance."""
        SSHPublicKey.__init__(self, opts, keydata, comment)
        (self._key_bits, 
        self._key_exponent, 
        self._key_modulus) = keydata.split(' ')
    @property
    def key(self):
        """Return just the SSH key data, without options or comments."""
        return '%s %s %s' % (self._key_bits, 
                             self._key_exponent, 
                             self._key_modulus)

class SSH2PublicKey(SSHPublicKey):
    """Class for representing an SSH public key, protocol version 2"""
    def __init__(self, opts, keydata, comment):
        """Create a new instance."""
        SSHPublicKey.__init__(self, opts, keydata, comment)
        (self._key_prefix, self._key_base64) = keydata.split(' ')
    @property
    def key(self):
        """Return just the SSH key data, without options or comments."""
        return '%s %s' % (self._key_prefix, self._key_base64)

def get_ssh_pubkey(line):
    """Take an SSH public key, and return an object representing it."""
    (opts, keydata, comment) = _explode_ssh_key(line)
    if keydata.startswith('ssh-'):
        return SSH2PublicKey(opts, keydata, comment)
    else:
        return SSH1PublicKey(opts, keydata, comment)

def _explode_ssh_key(line):
    """
    Break apart a public-key line correct.
    - Protocol 1 public keys consist of: 
      options, bits, exponent, modulus, comment. 
    - Protocol 2 public key consist of: 
      options, keytype, base64-encoded key, comment.
    - For all options that take an argument, having a quote inside the argument
      is valid, and should be in the file as '\"'
    - Spaces are also valid in those arguments.
    - Options must be seperated by commas.
    Seperately return the options, key data and comment.
    """
    opts = {}
    shl = shlex(StringIO(line), None, True)
    shl.wordchars += '-'
    # Treat ',' as whitespace seperation the options
    shl.whitespace += ','
    shl.whitespace_split = 1
    # Handle the options first
    keydata = None
    def _check_eof(tok):
        """See if the end was nigh."""
        if tok == shl.eof:
            raise MalformedSSHKey("Unexpected end of key")
    while True:
        tok = shl.get_token()
        _check_eof(tok)
        # This is the start of the actual key, protocol 1
        if tok.isdigit():
            keydata = tok
            expected_key_args = 2
            break
        # This is the start of the actual key, protocol 2
        if tok in SSH_KEY_PROTO2_TYPES:
            keydata = tok
            expected_key_args = 1
            break
        if tok in SSH_KEY_OPTS:
            opts[tok] = None
            continue
        if '=' in tok:
            (tok, _) = tok.split('=', 1)
            if tok in SSH_KEY_OPTS_WITH_ARGS:
                opts[tok] = _
                continue
        raise MalformedSSHKey("Unknown fragment %r" % (tok, ))
    # Now handle the key
    # Protocol 2 keys have only 1 argument besides the type
    # Protocol 1 keys have 2 arguments after the bit-count.
    shl.whitespace_split = 1
    while expected_key_args > 0:
        _ = shl.get_token()
        _check_eof(_)
        keydata += ' '+_
        expected_key_args -= 1
    # Everything that remains is a comment
    comment = ''
    shl.whitespace = ''
    while True:
        _ = shl.get_token()
        if _ == shl.eof or _ == None:
            break
        comment += _
    return (opts, keydata, comment)

_ACCEPTABLE_USER_RE = re.compile(
        r'^[a-zA-Z][a-zA-Z0-9_.-]*(@[a-zA-Z][a-zA-Z0-9.-]*)?$'
        )

def isSafeUsername(user):
    """Is the username safe to use a a filename? """
    match = _ACCEPTABLE_USER_RE.match(user)
    return (match is not None)

#X#key1 = 'no-X11-forwarding,command="x b c , d=e f \\"wham\\" \' 
#before you go-go" 
#ssh-rsa abc robbat2@foo foo\tbar#ignore'
#X#key2 = 'from=172.16.9.1 768 3 5 sam comment\tfoo'
#X#key3 = '768 3 5 commentfoo'
#X## 123456789 123456789 123456789 123456789 123456789
#X#k = get_ssh_pubkey(key1)
#X#print 'opts=%r' % (k.options, )
#X#print 'k=%r' % (k.key, )
#X#print 'c=%r' % (k.comment, )
#X#print 'u=%r' % (k.username, )
#X#print k.full_key
#X#
