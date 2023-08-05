FAQ
====

Q: Will encryption make my data safe?

A: Think of it as adding another layer of security, of itself not
being a complete solution. There are many issues involved in securing your
data, and encryption alone does not magically solve all of them. Security needs
to be considered at all stages in the process. The encryption provided (RSA + AES)
is genuinely strong encryption (and as such could cause problems). Key management
is the hard part.

Q: What if I think my private RSA private key is no longer private?

A: Obviously, try to avoid this situation. If it happens: 1) Generate a new
RSA key-pair, and then 2) `rotate()` the encryption on all files that were encrypted
using the public key associated with the compromised private key (see below on how
to rotate).

The meta-data includes information about what public key was used for
encryption, to make it easier to identify the relevant files. But even without that
information, you could just try rotate()'ing the encryption on all files, and it
would only succeed for those with the right key pair. The meta-data are not
required for key rotation. PsychoPy is not needed for rotation (or decryption).
Even opensslwrap is not needed: It is just a wrapper to make it easier to work with
standard, strong encryption tools (i.e., openssl).

Q: What if the internal (AES) password was disclosed (i.e., not the private
key but the one-time password that is used for the AES encryption)?

A: This is not very likely, and it would affect at most one file. Fix: Just `rotate()`
the encryption for that file--using the same keys is fine. That is, if you decrypt
and re-encrypt (i.e., rotate) with the same key pair, a new internal one-time password
will be generated during the re-encryption step. (The old AES password is not re-used,
ever, which is a crucial difference between the AES password and the RSA key pair.)

Q: What if I lose my private key?

A: The whole idea is that, if you don't have the private key, the encryption should
be strong enough that data recovery is a very expensive proposition, if its even
possible (and hopefully its not possible). You should design your procedures under
the assumption that data recovery will not be possible if you lose the private key.
If you do lose the key, resign yourself to the idea that your encrypted data are
going to stay encrypted forever. This is not at all to say that it is impossible
for the encryption to be compromised by someone, just that you should not plan on
being able to do it, or even hire someone to do it.
