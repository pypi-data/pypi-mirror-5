*evdev*
----------------------------------------

*evdev* provides bindings to the generic input event interface in Linux.
The *evdev* interface serves the purpose of passing events generated in the
kernel directly to userspace through character devices that are typically
located in ``/dev/input/``.

*evdev* also comes with bindings to *uinput*, the userspace input
subsystem. *Uinput* allows userspace programs to create and handle
input devices from which input events can be directly injected into
the input subsystem.


Documentation:
    http://packages.python.org/evdev

Development:
    https://github.com/gvalkov/python-evdev

PyPi:
    http://pypi.python.org/pypi/evdev


Changelog
=========

0.4.1 (Jul 24, 2013)
^^^^^^^^^^^

Fixes:
    - Fix reference counting in ``device_read``, ``device_read_many``
      and ``ioctl_capabilities``.


0.4.0 (Jul 01, 2013)
^^^^^^^^^^^^^^^^^^^^

Enhancements:
    - Add ``FF_*`` and ``FF_STATUS`` codes to ``ecodes`` (thanks @bgilbert).

    - Reverse event code mappings (``ecodes.{KEY,FF,REL,ABS}`` and
      etc.) will now map to a list of codes, whenever a value
      corresponds to multiple codes::

        >>> ecodes.KEY[152]
        ... ['KEY_COFFEE', 'KEY_SCREENLOCK']
        >>> ecodes.KEY[30]
        ... 'KEY_A'

    - Set the state of a LED through ``device.set_led()`` (thanks
      @accek). ``device.fd`` is opened in ``O_RDWR`` mode from now on.

Fixes:
    - Fix segfault in ``device_read_many()`` (thanks @bgilbert).

0.3.3 (May 29, 2013)
^^^^^^^^^^^^^^^^^^^^

Fixes:
    - Raise ``IOError`` from ``device_read()`` and ``device_read_many()`` when
      ``read()`` fails.

    - Several stability and style changes (thank you debian code reviewers).

0.3.2 (Apr 05, 2013)
^^^^^^^^^^^^^^^^^^^^

Fixes:
    - Fix vendor id and product id order in ``DeviceInfo`` (thanks @kived).

0.3.1 (Nov 23, 2012)
^^^^^^^^^^^^^^^^^^^^

Fixes:
    - ``device.read()`` will return an empty tuple if the device has
      nothing to offer (instead of segfaulting).

    - Exclude unnecessary package data in sdist and bdist.

0.3.0 (Nov 06, 2012)
^^^^^^^^^^^^^^^^^^^^

Enhancements:
    - Add ability to set/get auto-repeat settings with ``EVIOC{SG}REP``.

    - Add ``device.version`` - the value of ``EVIOCGVERSION``.

    - Add ``device.read_loop()``.

    - Add ``device.grab()`` and ``device.ungrab()`` - exposes ``EVIOCGRAB``.

    - Add ``device.leds`` - exposes ``EVIOCGLED``.

    - Replace ``DeviceInfo`` class with a namedtuple.

Fixes:
    - ``device.read_one()`` was dropping events.

    - Rename ``AbsData`` to ``AbsInfo`` (as in ``struct input_absinfo``).


0.2.0 (Aug 22, 2012)
^^^^^^^^^^^^^^^^^^^^

Enhancements:
    - Add the ability to set arbitrary device capabilities on uinput
      devices (defaults to all ``EV_KEY`` ecodes).

    - Add ``UInput.device`` which is an open ``InputDevice`` to the
      input device that uinput 'spawns'.

    - Add ``UInput.capabilities()`` which is just a shortcut to
      ``UInput.device.capabilities()``.

    - Rename ``UInput.write()`` to ``UInput.write_event()``.

    - Add a simpler ``UInput.write(type, code, value)`` method.

    - Make all ``UInput`` constructor arguments optional (default
      device name is now ``py-evdev-uinput``).

    - Add the ability to set ``absmin``, ``absmax``, ``absfuzz`` and
      ``absflat`` when specifying the uinput device's capabilities.

    - Remove the ``nophys`` argument - if a device fails the
      ``EVIOCGPHYS`` ioctl, phys will equal the empty string.

    - Make ``InputDevice.capabilities()`` perform a ``EVIOCGABS`` ioctl
      for devices that support ``EV_ABS`` and return that info wrapped in
      an ``AbsData`` namedtuple.

    - Split ``ioctl_devinfo`` into ``ioctl_devinfo`` and
      ``ioctl_capabilities``.

    - Split ``uinput_open()`` to ``uinput_open()`` and ``uinput_create()``

    - Add more uinput usage examples and documentation.

    - Rewrite uinput tests.

    - Remove ``mouserel`` and ``mouseabs`` from ``UInput``.

    - Tie the sphinx version and release to the distutils version.

    - Set 'methods-before-attributes' sorting in the docs.


Fixes:
    - Remove ``KEY_CNT`` and ``KEY_MAX`` from ``ecodes.keys``.


0.1.1 (May 18, 2012)
^^^^^^^^^^^^^^^^^^^^

Enhancements:
    - Add ``events.keys``, which is a combination of all ``BTN_`` and
      ``KEY_`` event codes.

Fixes:
    - ``ecodes.c`` was not generated when installing through ``pip``.


0.1.0 (May 17, 2012)
^^^^^^^^^^^^^^^^^^^^

*Initial Release*
