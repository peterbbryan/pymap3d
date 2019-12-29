"""geodetic transforms to auxilary coordinate systems involving latitude"""
import typing

from .ellipsoid import Ellipsoid
from .utils import sanitize

try:
    from numpy import radians, degrees, tan, sin, exp, pi, sqrt, inf, vectorize
    from numpy import arctan as atan, arcsinh as asinh, arctanh as atanh  # noqa: A001

    use_numpy = True
except ImportError:
    from math import atan, radians, degrees, tan, sin, asinh, atanh, exp, pi, sqrt, inf

    use_numpy = False

__all__ = [
    "geodetic2isometric",
    "isometric2geodetic",
    "geodetic2rectifying",
    "rectifying2geodetic",
    "geodetic2conformal",
    "conformal2geodetic",
    "geodetic2parametric",
    "parametric2geodetic",
    "geodetic2geocentric",
    "geocentric2geodetic",
    "geodetic2authalic",
    "authalic2geodetic",
]

if typing.TYPE_CHECKING:
    from numpy import ndarray


def geodetic2geocentric(geodetic_lat: "ndarray", ell: Ellipsoid = None, deg: bool = True) -> "ndarray":
    """
    convert geodetic latitude to geocentric latitude.

    like Matlab geocentricLatitude()

    Parameters
    ----------
    geodetic_lat : "ndarray"
        geodetic latitude
    ell : Ellipsoid, optional
         reference ellipsoid (default WGS84)
    deg : bool, optional
         degrees input/output  (False: radians in/out)

    Returns
    -------
    geocentric_lat : "ndarray"
         geocentric latiude

    Notes
    -----
    Equations from J. P. Snyder, "Map Projections - A Working Manual",
    US Geological Survey Professional Paper 1395, US Government Printing
    Office, Washington, DC, 1987, pp. 13-18.
    """
    geodetic_lat, ell = sanitize(geodetic_lat, ell, deg)

    geocentric_lat = atan((1 - (ell.eccentricity) ** 2) * tan(geodetic_lat))

    return degrees(geocentric_lat) if deg else geocentric_lat


def geocentric2geodetic(geocentric_lat: "ndarray", ell: Ellipsoid = None, deg: bool = True) -> "ndarray":
    """
    converts from geocentric latitude to geodetic latitude

    like Matlab geodeticLatitudeFromGeocentric()

    Parameters
    ----------
    geocentric_lat : "ndarray"
         geocentric latitude
    ell : Ellipsoid, optional
         reference ellipsoid (default WGS84)
    deg : bool, optional
         degrees input/output  (False: radians in/out)

    Returns
    -------
    geodetic_lat : "ndarray"
         geodetic latiude

    Notes
    -----
    Equations from J. P. Snyder, "Map Projections - A Working Manual",
    US Geological Survey Professional Paper 1395, US Government Printing
    Office, Washington, DC, 1987, pp. 13-18.
    """
    geocentric_lat, ell = sanitize(geocentric_lat, ell, deg)

    geodetic_lat = atan(tan(geocentric_lat) / (1 - (ell.eccentricity) ** 2))

    return degrees(geodetic_lat) if deg else geodetic_lat


def geodetic2isometric_point(geodetic_lat: float, ell: Ellipsoid = None, deg: bool = True) -> float:
    geodetic_lat, ell = sanitize(geodetic_lat, ell, deg)

    e = ell.eccentricity

    if abs(geodetic_lat - pi / 2) <= 1e-9:
        isometric_lat = inf
    elif abs(-geodetic_lat - pi / 2) <= 1e-9:
        isometric_lat = -inf
    else:
        isometric_lat = asinh(tan(geodetic_lat)) - e * atanh(e * sin(geodetic_lat))
        # same results
        # a1 = e * sin(geodetic_lat)
        # y = (1 - a1) / (1 + a1)
        # a2 = pi / 4 + geodetic_lat / 2
        # isometric_lat = log(tan(a2) * (y ** (e / 2)))
        # isometric_lat = log(tan(a2)) + e/2 * log((1-e*sin(geodetic_lat)) / (1+e*sin(geodetic_lat)))

    return degrees(isometric_lat) if deg else isometric_lat


def geodetic2isometric(geodetic_lat: "ndarray", ell: Ellipsoid = None, deg: bool = True) -> "ndarray":
    """
    computes isometric latitude on an ellipsoid


    like Matlab map.geodesy.IsometricLatitudeConverter.forward()

    Parameters
    ----------
    lat : "ndarray"
         geodetic latitude
    ell : Ellipsoid, optional
         reference ellipsoid (default WGS84)
    deg : bool, optional
         degrees input/output  (False: radians in/out)

    Returns
    -------
    isolat : "ndarray"
         isometric latiude

    Notes
    -----
    Isometric latitude is an auxiliary latitude proportional to the spacing
    of parallels of latitude on an ellipsoidal mercator projection.
    Based on Deakin, R.E., 2010, 'The Loxodrome on an Ellipsoid', Lecture Notes,
    School of Mathematical and Geospatial Sciences, RMIT University,
    January 2010
    """
    if use_numpy:
        fun = vectorize(geodetic2isometric_point)
        return fun(geodetic_lat, ell, deg)
    else:
        return geodetic2isometric_point(geodetic_lat, ell, deg)


def isometric2geodetic(isometric_lat: "ndarray", ell: Ellipsoid = None, deg: bool = True) -> "ndarray":
    """
    converts from isometric latitude to geodetic latitude

    like Matlab map.geodesy.IsometricLatitudeConverter.inverse()

    Parameters
    ----------
    isometric_lat : "ndarray"
         isometric latitude
    ell : Ellipsoid, optional
         reference ellipsoid (default WGS84)
    deg : bool, optional
         degrees input/output  (False: radians in/out)

    Returns
    -------
    geodetic_lat : "ndarray"
         geodetic latiude

    Notes
    -----
    Equations from J. P. Snyder, "Map Projections - A Working Manual",
    US Geological Survey Professional Paper 1395, US Government Printing
    Office, Washington, DC, 1987, pp. 13-18.
    """
    # NOT sanitize for isometric2geo
    if deg:
        isometric_lat = radians(isometric_lat)

    conformal_lat = 2 * atan(exp(isometric_lat)) - (pi / 2)
    geodetic_lat = conformal2geodetic(conformal_lat, ell, deg=False)

    return degrees(geodetic_lat) if deg else geodetic_lat


def conformal2geodetic(conformal_lat: "ndarray", ell: Ellipsoid = None, deg: bool = True) -> "ndarray":
    """
    converts from conformal latitude to geodetic latitude

    like Matlab map.geodesy.ConformalLatitudeConverter.inverse()

    Parameters
    ----------
    conformal_lat : "ndarray"
        conformal latitude
    ell : Ellipsoid, optional
        reference ellipsoid (default WGS84)
    deg : bool, optional
        degrees input/output  (False: radians in/out)

    Returns
    -------
    geodetic_lat : "ndarray"
        geodetic latiude

    Notes
    -----
    Equations from J. P. Snyder, "Map Projections - A Working Manual",
    US Geological Survey Professional Paper 1395, US Government Printing
    Office, Washington, DC, 1987, pp. 13-18.
    """
    conformal_lat, ell = sanitize(conformal_lat, ell, deg)

    e = ell.eccentricity
    f1 = e ** 2 / 2 + 5 * e ** 4 / 24 + e ** 6 / 12 + 13 * e ** 8 / 360
    f2 = 7 * e ** 4 / 48 + 29 * e ** 6 / 240 + 811 * e ** 8 / 11520
    f3 = 7 * e ** 6 / 120 + 81 * e ** 8 / 1120
    f4 = 4279 * e ** 8 / 161280

    geodetic_lat = (
        conformal_lat
        + f1 * sin(2 * conformal_lat)
        + f2 * sin(4 * conformal_lat)
        + f3 * sin(6 * conformal_lat)
        + f4 * sin(8 * conformal_lat)
    )

    return degrees(geodetic_lat) if deg else geodetic_lat


def geodetic2conformal(geodetic_lat: "ndarray", ell: Ellipsoid = None, deg: bool = True) -> "ndarray":
    """
    converts from geodetic latitude to conformal latitude

    like Matlab map.geodesy.ConformalLatitudeConverter.forward()

    Parameters
    ----------
    geodetic_lat : "ndarray"
         geodetic latitude
    ell : Ellipsoid, optional
         reference ellipsoid (default WGS84)
    deg : bool, optional
         degrees input/output  (False: radians in/out)

    Returns
    -------
    conformal_lat : "ndarray"
         conformal latiude

    Notes
    -----
    Equations from J. P. Snyder, "Map Projections - A Working Manual",
    US Geological Survey Professional Paper 1395, US Government Printing
    Office, Washington, DC, 1987, pp. 13-18.

    """
    if use_numpy:
        fun = vectorize(geodetic2conformal_point)
        return fun(geodetic_lat, ell, deg)
    else:
        return geodetic2conformal_point(geodetic_lat, ell, deg)


def geodetic2conformal_point(geodetic_lat: float, ell: Ellipsoid = None, deg: bool = True) -> float:
    geodetic_lat, ell = sanitize(geodetic_lat, ell, deg)

    e = ell.eccentricity
    f1 = 1 - e * sin(geodetic_lat)
    f2 = 1 + e * sin(geodetic_lat)
    f3 = 1 - sin(geodetic_lat)
    f4 = 1 + sin(geodetic_lat)

    #  compute conformal latitudes with correction for points at +90
    try:
        conformal_lat = 2 * atan(sqrt((f4 / f3) * ((f1 / f2) ** e))) - (pi / 2)
    except ZeroDivisionError:
        conformal_lat = pi / 2

    return degrees(conformal_lat) if deg else conformal_lat


# %% rectifying
def geodetic2rectifying(geodetic_lat: "ndarray", ell: Ellipsoid = None, deg: bool = True) -> "ndarray":
    """
    converts from geodetic latitude to rectifying latitude

    like Matlab map.geodesy.RectifyingLatitudeConverter.forward()

    Parameters
    ----------
    geodetic_lat : "ndarray"
         geodetic latitude
    ell : Ellipsoid, optional
         reference ellipsoid (default WGS84)
    deg : bool, optional
         degrees input/output  (False: radians in/out)

    Returns
    -------
    rectifying_lat : "ndarray"
         rectifying latiude

    Notes
    -----
    Equations from J. P. Snyder, "Map Projections - A Working Manual",
    US Geological Survey Professional Paper 1395, US Government Printing
    Office, Washington, DC, 1987, pp. 13-18.

    """
    geodetic_lat, ell = sanitize(geodetic_lat, ell, deg)

    n = ell.thirdflattening
    f1 = 3 * n / 2 - 9 * n ** 3 / 16
    f2 = 15 * n ** 2 / 16 - 15 * n ** 4 / 32
    f3 = 35 * n ** 3 / 48
    f4 = 315 * n ** 4 / 512

    rectifying_lat = (
        geodetic_lat
        - f1 * sin(2 * geodetic_lat)
        + f2 * sin(4 * geodetic_lat)
        - f3 * sin(6 * geodetic_lat)
        + f4 * sin(8 * geodetic_lat)
    )

    return degrees(rectifying_lat) if deg else rectifying_lat


def rectifying2geodetic(rectifying_lat: "ndarray", ell: Ellipsoid = None, deg: bool = True) -> "ndarray":
    """
    converts from rectifying latitude to geodetic latitude

    like Matlab map.geodesy.RectifyingLatitudeConverter.inverse()

    Parameters
    ----------
    rectifying_lat : "ndarray"
        latitude
    ell : Ellipsoid, optional
        reference ellipsoid (default WGS84)
    deg : bool, optional
        degrees input/output  (False: radians in/out)

    Returns
    -------
    geodetic_lat : "ndarray"
        geodetic latiude

    Notes
    -----
    Equations from J. P. Snyder, "Map Projections - A Working Manual",
    US Geological Survey Professional Paper 1395, US Government Printing
    Office, Washington, DC, 1987, pp. 13-18.
    """
    rectifying_lat, ell = sanitize(rectifying_lat, ell, deg)

    n = ell.thirdflattening
    f1 = 3 * n / 2 - 27 * n ** 3 / 32
    f2 = 21 * n ** 2 / 16 - 55 * n ** 4 / 32
    f3 = 151 * n ** 3 / 96
    f4 = 1097 * n ** 4 / 512

    geodetic_lat = (
        rectifying_lat
        + f1 * sin(2 * rectifying_lat)
        + f2 * sin(4 * rectifying_lat)
        + f3 * sin(6 * rectifying_lat)
        + f4 * sin(8 * rectifying_lat)
    )

    return degrees(geodetic_lat) if deg else geodetic_lat


# %% authalic
def geodetic2authalic(geodetic_lat: "ndarray", ell: Ellipsoid = None, deg: bool = True) -> "ndarray":
    """
    converts from geodetic latitude to authalic latitude

    like Matlab map.geodesy.AuthalicLatitudeConverter.forward()

    Parameters
    ----------
    geodetic_lat : "ndarray"
         geodetic latitude
    ell : Ellipsoid, optional
         reference ellipsoid (default WGS84)
    deg : bool, optional
         degrees input/output  (False: radians in/out)

    Returns
    -------
    authalic_lat : "ndarray"
         authalic latiude

    Notes
    -----
    Equations from J. P. Snyder, "Map Projections - A Working Manual",
    US Geological Survey Professional Paper 1395, US Government Printing
    Office, Washington, DC, 1987, pp. 13-18.

    """
    geodetic_lat, ell = sanitize(geodetic_lat, ell, deg)

    e = ell.eccentricity
    f1 = e ** 2 / 3 + 31 * e ** 4 / 180 + 59 * e ** 6 / 560
    f2 = 17 * e ** 4 / 360 + 61 * e ** 6 / 1260
    f3 = 383 * e ** 6 / 45360

    authalic_lat = geodetic_lat - f1 * sin(2 * geodetic_lat) + f2 * sin(4 * geodetic_lat) - f3 * sin(6 * geodetic_lat)

    return degrees(authalic_lat) if deg else authalic_lat


def authalic2geodetic(authalic_lat: "ndarray", ell: Ellipsoid = None, deg: bool = True) -> "ndarray":
    """
    converts from authalic latitude to geodetic latitude

    like Matlab map.geodesy.AuthalicLatitudeConverter.inverse()

    Parameters
    ----------
    authalic_lat : "ndarray"
        latitude
    ell : Ellipsoid, optional
        reference ellipsoid (default WGS84)
    deg : bool, optional
        degrees input/output  (False: radians in/out)

    Returns
    -------
    geodetic_lat : "ndarray"
        geodetic latiude

    Notes
    -----
    Equations from J. P. Snyder, "Map Projections - A Working Manual",
    US Geological Survey Professional Paper 1395, US Government Printing
    Office, Washington, DC, 1987, pp. 13-18.
    """
    authalic_lat, ell = sanitize(authalic_lat, ell, deg)
    e = ell.eccentricity
    f1 = e ** 2 / 3 + 31 * e ** 4 / 180 + 517 * e ** 6 / 5040
    f2 = 23 * e ** 4 / 360 + 251 * e ** 6 / 3780
    f3 = 761 * e ** 6 / 45360

    geodetic_lat = authalic_lat + f1 * sin(2 * authalic_lat) + f2 * sin(4 * authalic_lat) + f3 * sin(6 * authalic_lat)

    return degrees(geodetic_lat) if deg else geodetic_lat


# %% parametric
def geodetic2parametric(geodetic_lat: "ndarray", ell: Ellipsoid = None, deg: bool = True) -> "ndarray":
    """
    converts from geodetic latitude to parametric latitude

    like Matlab parametriclatitude()

    Parameters
    ----------
    geodetic_lat : "ndarray"
         geodetic latitude
    ell : Ellipsoid, optional
         reference ellipsoid (default WGS84)
    deg : bool, optional
         degrees input/output  (False: radians in/out)

    Returns
    -------
    parametric_lat : "ndarray"
         parametric latiude

    Notes
    -----
    Equations from J. P. Snyder, "Map Projections - A Working Manual",
    US Geological Survey Professional Paper 1395, US Government Printing
    Office, Washington, DC, 1987, pp. 13-18.

    """
    geodetic_lat, ell = sanitize(geodetic_lat, ell, deg)

    parametric_lat = atan(sqrt(1 - (ell.eccentricity) ** 2) * tan(geodetic_lat))

    return degrees(parametric_lat) if deg else parametric_lat


def parametric2geodetic(parametric_lat: "ndarray", ell: Ellipsoid = None, deg: bool = True) -> "ndarray":
    """
    converts from parametric latitude to geodetic latitude

    like Matlab geodeticLatitudeFromParametric()

    Parameters
    ----------
    parametric_lat : "ndarray"
        latitude
    ell : Ellipsoid, optional
        reference ellipsoid (default WGS84)
    deg : bool, optional
        degrees input/output  (False: radians in/out)

    Returns
    -------
    geodetic_lat : "ndarray"
        geodetic latiude

    Notes
    -----
    Equations from J. P. Snyder, "Map Projections - A Working Manual",
    US Geological Survey Professional Paper 1395, US Government Printing
    Office, Washington, DC, 1987, pp. 13-18.
    """
    parametric_lat, ell = sanitize(parametric_lat, ell, deg)

    geodetic_lat = atan(tan(parametric_lat) / sqrt(1 - (ell.eccentricity) ** 2))

    return degrees(geodetic_lat) if deg else geodetic_lat
