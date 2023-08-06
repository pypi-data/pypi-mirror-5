# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def sdss_flagval(flagname,bitname):
    """Convert bitmask names into values.

    Converts human-readable bitmask names into numerical values.  The inputs
    are not case-sensitive; all inputs are converted to upper case internally.

    Parameters
    ----------
    flagname : str
        The name of a bitmask group.
    bitname : str or list
        The name(s) of the specific bitmask(s) within the `flagname` group.

    Returns
    -------
    sdss_flagval : long
        The value of the bitmask name(s).

    Raises
    ------
    KeyError
        If `flagname` or `bitname` are invalid names.

    Examples
    --------
    >>> pydl.pydlutils.sdss.sdss_flagval('ANCILLARY_TARGET1',['BLAZGX','ELG','BRIGHTGAL'])
    2310346608843161600L
    """
    from . import maskbits
    #
    # Make sure inlabel is a list
    #
    if isinstance(bitname,str):
        bitnames = [bitname.upper()]
    else:
        bitnames = [b.upper() for b in bitname]
    flagu = flagname.upper()
    flagvalue = 0L
    for bit in bitnames:
        if flagu in maskbits:
            if bit in maskbits[flagu]:
                flagvalue += 2L**maskbits[flagu][bit]
            else:
                raise KeyError("Unknown bit label {0} for flag group {1}!".format(bit, flagu))
        else:
            raise KeyError("Unknown flag group {0}!".format(flagu))
    return flagvalue
