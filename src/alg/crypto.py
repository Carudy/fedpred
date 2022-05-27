import nacl.utils
from nacl.signing import SigningKey, VerifyKey
import nacl.encoding
import nacl.hash
import nacl.secret
from nacl import pwhash


def gen_sign_key():
    signing_key = SigningKey.generate()
    verify_key = signing_key.verify_key
    return signing_key, verify_key.encode()


def verify_sign(verify_key, sign, msg):
    vk = VerifyKey(verify_key)
    return vk.verify(sign) == msg


def sha256(msg):
    digest = nacl.hash.sha256(msg, encoder=nacl.encoding.HexEncoder)
    return digest


def kdf(pwd, salt):
    if len(salt) < pwhash.argon2i.SALTBYTES:
        salt = salt.decode()
        salt = salt * int(pwhash.argon2i.SALTBYTES / len(salt) + 1)
        salt = salt.encode()
    salt = salt[:pwhash.argon2i.SALTBYTES]
    ops = pwhash.argon2i.OPSLIMIT_SENSITIVE
    mem = pwhash.argon2i.MEMLIMIT_SENSITIVE
    key = pwhash.argon2i.kdf(nacl.secret.SecretBox.KEY_SIZE, pwd, salt,
                             opslimit=ops, memlimit=mem)
    return key


def kdf_box(pwd, salt):
    return nacl.secret.SecretBox(kdf(pwd, salt))
