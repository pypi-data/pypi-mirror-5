"""The EE Javascript library."""



# Using lowercase function naming to match the JavaScript names.
# pylint: disable-msg=g-bad-name

import datetime
import numbers

import oauth2client.client

from apifunction import ApiFunction
from collection import Collection
from computedobject import ComputedObject
from customfunction import CustomFunction
import data
from ee_exception import EEException
import ee_types as types
from encodable import Encodable
from feature import Feature
from featurecollection import FeatureCollection
from filter import Filter
from function import Function
from geometry import Geometry
from image import Image
from imagecollection import ImageCollection
from serializer import Serializer


OAUTH2_SCOPE = 'https://www.googleapis.com/auth/earthengine.readonly'


def Initialize(credentials=None, opt_url=None):
  """Initialize the EE library.

  If this hasn't been called by the time any object constructor is used,
  it will be called then.  If this is called a second time with a different
  URL, this doesn't do an un-initialization of e.g.: the previously loaded
  Algorithms, but will overwrite them and let point at alternate servers.

  Args:
    credentials: OAuth2 or ClientLogin credentials.
    opt_url: The base url for the EarthEngine REST API to connect to.
  """
  data.CREDENTIALS = credentials
  if opt_url is None:
    base_url = 'https://earthengine.googleapis.com/api'
    tile_url = 'https://earthengine.googleapis.com'
  else:
    base_url = opt_url + '/api'
    tile_url = opt_url
  data.setBaseUrls(base_url, tile_url)

  # Initialize the dynamically loaded functions on the objects that want them.
  ApiFunction.initialize()
  Image.initialize()
  Feature.initialize()
  Collection.initialize()
  ImageCollection.initialize()
  FeatureCollection.initialize()
  Filter.initialize()


def Reset():
  """Reset the library. Useful for re-initializing to a different server."""
  ApiFunction.reset()
  Image.reset()
  Feature.reset()
  Collection.reset()
  ImageCollection.reset()
  FeatureCollection.reset()
  Filter.reset()


def ServiceAccountCredentials(email, key_file):
  """Configure OAuth2 credentials for a Google Service Account.

  Args:
    email: The email address of the account for which to configure credentials.
    key_file: The path to a file containing the private key associated with
        the service account.

  Returns:
    An OAuth2 credentials object.
  """
  private_key = open(key_file).read()
  return oauth2client.client.SignedJwtAssertionCredentials(
      email, private_key, OAUTH2_SCOPE)


def call(func, *args, **kwargs):
  """Invoke the given algorithm with the specified args.

  Args:
    func: The function to call. Either an ee.Function object or the name of
        an API function.
    *args: The positional arguments to pass to the function.
    **kwargs: The named arguments to pass to the function.

  Returns:
    A ComputedObject representing the called function. If the signature
    specifies a recognized return type, the returned value will be cast
    to that type.
  """
  if isinstance(func, basestring):
    func = ApiFunction.lookup(func)
  return func.call(*args, **kwargs)


def apply(func, named_args):  # pylint: disable-msg=redefined-builtin
  """Call a function with a dictionary of named arguments.

  Args:
    func: The function to call. Either an ee.Function object or the name of
        an API function.
    named_args: A dictionary of arguments to the function.

  Returns:
    A ComputedObject representing the called function. If the signature
    specifies a recognized return type, the returned value will be cast
    to that type.
  """
  if isinstance(func, basestring):
    func = ApiFunction.lookup(func)
  return func.apply(named_args)


def _Promote(arg, klass):
  """Wrap an argument in an object of the specified class.

  This is used to e.g.: promote numbers or strings to Images and arrays
  to Collections.

  Args:
    arg: The object to promote.
    klass: The expected type.

  Returns:
    The argument promoted if the class is recognized, otherwise the
    original argument.
  """
  if arg is None:
    return arg

  if klass == 'Image':
    return Image(arg)
  elif klass == 'ImageCollection':
    return ImageCollection(arg)
  elif klass in ('Feature', 'EEObject'):
    if isinstance(arg, Collection):
      # TODO(user): Decide whether we want to leave this in. It can be
      #              quite dangerous on large collections.
      return ApiFunction.call_(
          'Feature', ApiFunction.call_('ExtractGeometry', arg))
    else:
      return Feature(arg)
  elif klass in ('ProjGeometry', 'Geometry'):
    if isinstance(arg, Collection):
      return ApiFunction.call_('ExtractGeometry', arg)
    if isinstance(arg, ComputedObject):
      return arg
    else:
      return Geometry(arg)
  elif klass in ('FeatureCollection', 'EECollection', 'Collection'):
    if isinstance(arg, Collection):
      return arg
    else:
      return FeatureCollection(arg)
  elif klass == 'Filter':
    return Filter(arg)
  elif klass == 'ErrorMargin' and isinstance(arg, numbers.Number):
    return ApiFunction.call_('ErrorMargin', arg, 'meters')
  elif klass == 'Algorithm' and isinstance(arg, basestring):
    return ApiFunction.lookup(arg)
  elif klass == 'Date':
    if isinstance(arg, basestring):
      try:
        import dateutil.parser    # pylint: disable-msg=g-import-not-at-top
      except ImportError:
        raise EEException(
            'Conversion of strings to dates requires the dateutil library.')
      else:
        return dateutil.parser.parse(arg)
    elif isinstance(arg, numbers.Number):
      return datetime.datetime.fromtimestamp(arg / 1000)
    else:
      return arg
  else:
    return arg


# Set up type promotion rules as soon the package is loaded.
Function._registerPromoter(_Promote)   # pylint: disable-msg=protected-access
