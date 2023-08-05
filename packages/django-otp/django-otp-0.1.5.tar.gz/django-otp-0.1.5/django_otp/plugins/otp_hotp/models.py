from binascii import unhexlify

from django.db import models

from django_otp.models import Device
from django_otp.oath import hotp
from django_otp.util import random_hex, hex_validator


class HOTPDevice(Device):
    """
    A generic HOTP :class:`~django_otp.models.Device`. The model fields mostly
    correspond to the arguments to :func:`django_otp.oath.hotp`. They all have
    sensible defaults, including the key, which is randomly generated.

    .. attribute:: key

        *CharField*: A hex-encoded secret key of up to 40 bytes. (Default: 20
        random bytes)

    .. attribute:: digits

        *PositiveSmallIntegerField*: The number of digits to expect from the
        token generator (6 or 8). (Default: 6)

    .. attribute:: tolerance

        *PositiveSmallIntegerField*: The number of missed tokens to tolerate.
        (Default: 5)

    .. attribute:: counter

        *BigIntegerField*: The next counter value to expect. (Initial: 0)
    """
    key = models.CharField(max_length=80, validators=[hex_validator()], default=lambda: random_hex(20), help_text=u"A hex-encoded secret key of up to 40 bytes.")
    digits = models.PositiveSmallIntegerField(choices=[(6,6), (8,8)], default=6, help_text=u"The number of digits to expect in a token.")
    tolerance = models.PositiveSmallIntegerField(default=5, help_text=u"The number of missed tokens to tolerate.")
    counter = models.BigIntegerField(default=0, help_text=u"The next counter value to expect.")

    class Meta(Device.Meta):
        verbose_name = u"HOTP device"

    @property
    def bin_key(self):
        """
        The secret key as a binary string.
        """
        return unhexlify(self.key)

    def verify_token(self, token):
        try:
            token = int(token)
        except StandardError:
            verified = False
        else:
            key = self.bin_key

            for counter in range(self.counter, self.counter + self.tolerance + 1):
                if hotp(key, counter, self.digits) == token:
                    verified = True
                    self.counter = counter + 1
                    self.save()
                    break
            else:
                verified = False

        return verified
