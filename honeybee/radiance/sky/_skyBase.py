from abc import ABCMeta, abstractproperty, abstractmethod


class RadianceSky(object):
    """Base class for Honeybee Skies."""
    __metaclass__ = ABCMeta
    __slots__ = ()

    @classmethod
    def fromJson(cls):
        raise NotImplementedError(
            "fromJson is not implemented for {}.".format(cls.__class__.__name__)
        )

    @property
    def isRadianceSky(self):
        """Return True for skies."""
        return True

    @property
    def isPointInTime(self):
        """Return True if the sky is generated for a single poin in time."""
        return False

    @abstractproperty
    def isClimateBased(self):
        """Return True if the sky is created based on values from weather file."""
        pass

    @abstractmethod
    def toRadString(self):
        """Return radiance definition as a string."""
        pass

    @abstractmethod
    def execute(self, filepath):
        """Execute the sky and write the results to a file if desired."""
        pass
