# -*- mode: yaml -*-

# This script builds a debian live image
# to be netbooted.
/usr/local/bin/build-live-images:
  file.managed:
    - source: salt://scripts/make-live-image.sh
    - user: root
    - group: root
    - mode: 755

# FIXME
# IMPORTANT
# this script, as well as the script for jessie
# are run directly by the salt-minion.
/usr/local/bin/build-keyring-package:
  file.managed:
    - source: salt://scripts/build-keyring-package.sh
    - user: root
    - group: root
    - mode: 755
  



# These scripts are used during development
# and have limited usefulness otherwise.
/usr/local/bin/recreate-paella-database:
  file.managed:
    - source: salt://files/recreate-paella-database
    - mode: 755
    - template: mako


# This script has been handy in developing the
# live images.
/usr/local/bin/destroy-livebuild-states:
  file.managed:
    - source: salt://scripts/destroy-livebuild-states.sh
    - mode: 755

# This script was used to generate the gpg key
# to be used to sign the partial debian mirror.
# The original idea was to generate a different
# key each time, but the time to configure that
# method required more time the perceived
# benefit returned.  A fake RNG needed to be
# used to gather the "fake entropy" required
# to make a good key.  I decided instead of
# having people possibly use untrustworthy
# keys due to not knowing the details of the
# key generation, I would just create a single
# gpg key that I mark as insecure.
/usr/local/bin/generate-gpg-key:
  file.managed:
    - source: salt://files/generate-gpg-key
    - user: root
    - group: root
    - mode: 755

