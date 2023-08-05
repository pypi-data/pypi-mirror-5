"""A class for representing built-in EE API Function.

Earth Engine can dynamically produce a JSON array listing the
algorithms available to the user.  Each item in the dictionary identifies
the name and return type of the algorithm, the name and type of its
arguments, whether they're required or optional, default values and docs
for each argument and the algorithms as a whole.

This class manages the algorithm dictionary and creates JavaScript functions
to apply each EE algorithm.
"""



# Using lowercase function naming to match the JavaScript names.
# pylint: disable-msg=g-bad-name

import copy
import keyword
import re

import data
import ee_exception
import ee_types
import function


class ApiFunction(function.Function):
  """An object representing an EE API Function."""

  # A dictionary of functions defined by the API server.
  _api = None

  def __init__(self, name, opt_signature=None):
    """Creates a function defined by the EE API.

    Args:
      name: The name of the function.
      opt_signature: The signature of the function. If unspecified,
          looked up dynamically.
    """
    if opt_signature is None:
      opt_signature = ApiFunction.lookup(name).getSignature()

    # The signature of this API function.
    self._signature = copy.deepcopy(opt_signature)
    self._signature['name'] = name

  def __eq__(self, other):
    return (isinstance(other, ApiFunction) and
            self.getSignature() == other.getSignature())

  def __ne__(self, other):
    return not self.__eq__(other)

  @classmethod
  def call_(cls, name, *args, **kwargs):
    """Call a named API function with positional and keyword arguments.

    Args:
      name: The name of the API function to call.
      *args: Positional arguments to pass to the function.
      **kwargs: Keyword arguments to pass to the function.

    Returns:
      An object representing the called function. If the signature specifies
      a recognized return type, the returned value will be cast to that type.
    """
    return cls.lookup(name).call(*args, **kwargs)

  @classmethod
  def apply_(cls, name, named_args):
    """Call a named API function with a dictionary of named arguments.

    Args:
      name: The name of the API function to call.
      named_args: A dictionary of arguments to the function.

    Returns:
      An object representing the called function. If the signature specifies
      a recognized return type, the returned value will be cast to that type.
    """
    return cls.lookup(name).apply(named_args)

  def encode(self, unused_encoder):
    return self._signature['name']

  def getSignature(self):
    """Returns a description of the interface provided by this function."""
    return self._signature

  @classmethod
  def allSignatures(cls):
    """Returns a map from the name to signature for all API functions."""
    cls.initialize()
    return {name: func.getSignature() for name, func in cls._api.iteritems()}

  @classmethod
  def lookup(cls, name):
    """Looks up an API function by name.

    Args:
      name: The name of the function to get.

    Returns:
      The requested ApiFunction.
    """
    cls.initialize()
    if name not in cls._api:
      raise ee_exception.EEException(
          'Unknown built-in function name: %s' % name)
    return cls._api[name]

  @classmethod
  def initialize(cls):
    """Initializes the list of signatures from the Earth Engine front-end."""
    if not cls._api:
      signatures = data.getAlgorithms()
      api = {}
      for name, sig in signatures.iteritems():
        # Strip type parameters.
        sig['returns'] = re.sub('<.*>', '', sig['returns'])
        for arg in sig['args']:
          arg['type'] = re.sub('<.*>', '', arg['type'])
        api[name] = cls(name, sig)
      cls._api = api

  @classmethod
  def reset(cls):
    """Clears the API functions list so it will be reloaded from the server."""
    cls._api = None

  @classmethod
  def importApi(cls, target, prefix, type_name, opt_prepend=None):
    """Adds all API functions that begin with a given prefix to a target class.

    Args:
      target: The class to add to.
      prefix: The prefix to search for in the signatures.
      type_name: The name of the object's type. Functions whose
          first argument matches this type are bound as instance methods, and
          those whose first argument doesn't match are bound as static methods.
      opt_prepend: An optional string to prepend to the names of the
          added functions.
    """
    cls.initialize()
    prepend = opt_prepend or ''
    for name, api_func in cls._api.iteritems():
      parts = name.split('.')
      if len(parts) == 2 and parts[0] == prefix:
        fname = prepend + parts[1]
        signature = api_func.getSignature()

        # Specifically handle the function names that are illegal in python.
        if keyword.iskeyword(fname):
          fname = fname.title()

        # Don't overwrite existing versions of this function.
        if hasattr(target, fname):
          fname = '_' + fname

        # Create a new function so we can attach properties to it.
        def MakeBoundFunction(func):
          # We need the lambda to capture "func" from the enclosing scope.
          # pylint: disable-msg=unnecessary-lambda
          return lambda *args, **kwargs: func.call(*args, **kwargs)
          # pylint: enable-msg=unnecessary-lambda
        bound_function = MakeBoundFunction(api_func)

        # Add docs.
        setattr(bound_function, '__name__', name.encode('utf8'))
        bound_function.__doc__ = str(api_func)
        # Attach the signature object for documentation generators.
        bound_function.signature = signature

        # Decide whether this is a static or an instance function.
        is_instance = (signature['args'] and
                       ee_types.isSubtype(signature['args'][0]['type'],
                                          type_name))
        if not is_instance:
          bound_function = staticmethod(bound_function)

        # Attach the function as a method.
        setattr(target, fname, bound_function)

  @staticmethod
  def clearApi(target):
    """Removes all methods added by importApi() from a target class.

    Args:
      target: The class to remove from.
    """
    for attr_name in dir(target):
      attr_value = getattr(target, attr_name)
      if callable(attr_value) and hasattr(attr_value, 'signature'):
        delattr(target, attr_name)
