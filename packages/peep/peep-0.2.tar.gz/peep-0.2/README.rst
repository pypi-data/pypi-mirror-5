====
Peep
====

Historically, deploying Python projects has been a pain in the neck if you want
any kind of security. PyPI lets package authors change the contents of their
packages without revving the version number, and, until very recently, there
was no support for HTTPS, leaving it open to man-in-the-middle attacks. If you
wanted to guarantee known-good dependencies for your deployment, you had to
either run a local PyPI mirror, manually uploading packages as you vetted them,
or you had to check everything into a vendor library, necessitating a lot of
fooling around with your VCS (or maintaining custom tooling) to do upgrades.

Peep fixes all that.

Vet your packages, put hashes of the PyPI-sourced tarballs into
requirements.txt, use ``peep install`` instead of ``pip install``, and let the
crypto do the rest. If a downloaded package doesn't match the hash, ``peep``
will freak out, and installation will go no further. No servers to maintain, no
enormous vendor libs to wrestle. Just requirements.txt with some funny-looking
comments and peace of mind.


Switching to Peep
=================

1. Use ``peep install -r requirements.txt`` to install your project once.
   You'll get output like this::

    <a bunch of pip output>

    The following packages had no hashes specified in the requirements file,
    which leaves them open to tampering. Vet these packages to your
    satisfaction, then add these "sha256" lines like so:

        # sha256: qF4YU3XbdcEJ-Z7N49VUFfA15waKgiUs9PFsZnrDj0k
        Jinja2==x.y.z

        # sha256: u_8C3DCeUoRt2WPSlIOnKV_MAhYkc40zNZxDlxCA-as
        Pygments==x.y.z

        # sha256: EIw9QftwHEr07wDo677cFHYyyCJHvreYyNhlehKBAgY
        Werkzeug==x.y.z

        # sha256: FWvz7Ce6nsfgz4--AoCHGAmdIY3kA-tkpxTXO6GimrE
        requests==x.y.z

    Not proceeding to installation.
2. Vet the packages coming off PyPI in whatever way you typically do.
3. Add the recommended hash lines to your requirements.txt, each one
   directly above the requirement it applies to. (The hashes are of the
   original, compressed tarballs from PyPI.)
4. In the future, always use ``peep install`` to install your project. You are
   now cryptographically safe!


The Fearsome Warning
====================

If, during installation, a hash doesn't match, ``peep`` will say something like
this::

    THE FOLLOWING PACKAGES DIDN'T MATCHES THE HASHES SPECIFIED IN THE
    REQUIREMENTS FILE. If you have updated the package versions, update the
    hashes. If not, freak out, because someone has tampered with the packages.

        futures: expected goofYhddA1kUpMLVODNbhIgHfQn88vioPHLwayTyqwOJEgY
                      got YhddA1kUpMLVODNbhIgHfQn88vioPHLwayTyqwOJEgY

...and will exit with a status of 1. Freak out appropriately.


Other Niceties
==============

* ``peep`` implicitly turns on pip's ``--no-deps`` option, because obviously
  you'll need to list all your packages in your requirements file in order to
  specify hashes for all of them.
* All non-install commands just fall through to pip, so you can use ``peep``
  all the time if you want. This comes in handy for existing scripts that have
  a big ``$PIP=/path/to/pip`` at the top.
* ``peep``-compatible requirements files remain entirely usable with ``pip``,
  because the hashes are just comments, after all.


Version History
===============

0.2
  * Fix repeated-logging bug.
  * Fix spurious error message about not having any requirements files.
  * Pass pip's exit code through to the outside for calls to non-``install``
    subcommands.
  * Improve spacing in the final output.


0.1
  * Proof of concept. Does all the crypto stuff. Should be secure. Some rough
    edges in the UI.
