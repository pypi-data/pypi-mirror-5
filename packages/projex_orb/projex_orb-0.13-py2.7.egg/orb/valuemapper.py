""" [desc] """

# define authorship information
__authors__         = ['Eric Hulser']
__author__          = ','.join(__authors__)
__credits__         = []
__copyright__       = 'Copyright (c) 2011, Projex Software, LLC'
__license__         = 'LGPL'

__maintainer__      = 'Projex Software, LLC'
__email__           = 'team@projexsoftware.com'

import projex.text

class ValueMapper(object):
    """
    Handles safe mapping of record values to database values.
    """
    _mappers = []
    
    def mapValue(self, value):
        """
        Converts the inputed value to a safe value.
        
        :param      value | <variant>
        
        :return     <variant>
        """
        return value
    
    @staticmethod
    def mappers():
        """
        Returns the registered value mappers for the system.
        
        :return     [<ValueMapper>, ..]
        """
        return ValueMapper._mappers
    
    @staticmethod
    def mappedValue( value ):
        """
        Returns a mapped value for this instance from the given value through
        all the ValueWrapper plugins.
        
        :param      value | <variant>
        
        :return     <variant>
        """
        for mapper in ValueMapper.mappers():
            value = mapper.mapValue(value)
        return value
    
    @staticmethod
    def register(mapper):
        """
        Registers a ValueMapper class to the system.
        
        :param      mapper | <ValueMapper>
        """
        ValueMapper._mappers.append(mapper)

#------------------------------------------------------------------------------

class QtValueMapper(ValueMapper):
    """
    Maps Qt values to standard python values.
    """
    def mapValue(self, value):
        """
        Converts the inputed value to a safe value.
        
        :param      value | <variant>
        
        :return     <variant>
        """
        val_name = type(value).__name__
        
        if ( val_name == 'QString' ):
            return projex.text.encoded(value)
        elif ( val_name == 'QVariant' ):
            return value.toPyObject()
        elif ( val_name == 'QDate' ):
            return value.toPyDate()
        elif ( val_name == 'QDateTime' ):
            return value.toPyDateTime()
        elif ( val_name == 'QTime' ):
            return value.toPyTime()
        elif ( val_name == 'QColor' ):
            return value.name()
        return value

ValueMapper.register(QtValueMapper())