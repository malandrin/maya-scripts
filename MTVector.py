#-------------------------------------------------------------
#-- vector 3 class
#-------------------------------------------------------------
from math import *

def AutoFloatProperties( *props ):
    '''metaclass'''
    class _AutoFloatProperties( type ):
        def __init__( cls, name, bases, cdict ):
            super( _AutoFloatProperties, cls ).__init__( name, bases, cdict )
            for attr in props:
                def fget( self, _attr='_'+attr ): return getattr( self, _attr )
                def fset( self, value, _attr='_'+attr ): setattr( self, _attr, float( value ) )
                setattr( cls, attr, property( fget, fset ) )
    return _AutoFloatProperties

#-------------------------------------------------------------
#--
#-------------------------------------------------------------	
class MTVector:	
	__metaclass__ = AutoFloatProperties( 'x','y','z' )
	
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def __init__( self, x, y, z ):
		self.x = x
		self.y = y
		self.z = z

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------			
	def Clone( self ):
		return MTVector( self.x, self.y, self.z )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def __eq__( self, other ):
		return ( ( self.x == other.x ) and ( self.y == other.y ) and ( self.z == other.z ) )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def __ne__( self, other ):
		return not self.__eq__( self, other )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def __add__( self, other ):
		return MTVector( self.x + other.x, self.y + other.y, self.z + other.z )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def __iadd__( self, other ):
		self.x += other.x
		self.y += other.y
		self.z += other.z
		
		return self

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __sub__( self, other ):
		return MTVector( self.x - other.x, self.y - other.y, self.z - other.z )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __isub__( self, other ):
		self.x -= other.x
		self.y -= other.y
		self.z -= other.z
		
		return self
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------		
	def __mul__( self, other ):
		if ( isinstance( other, MTVector ) ):
			return MTVector( self.x * other.x, self.y * other.y, self.z * other.z )
		
		return MTVector( self.x * other, self.y * other, self.z * other )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __imul__( self, other ):
		if ( isinstance( other, MTVector ) ):
			self.x *= other.x
			self.y *= other.y
			self.z *= other.z
		else:
			self.x *= other
			self.y *= other
			self.z *= other
		
		return self
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------		
	def __div__( self, other ):
		if ( isinstance( other, MTVector ) ):
			return MTVector( self.x / other.x, self.y / other.y, self.z / other.z )
		
		return MTVector( self.x / other, self.y / other, self.z / other )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __idiv__( self, other ):
		if ( isinstance( other, MTVector ) ):
			self.x /= other.x
			self.y /= other.y
			self.z /= other.z
		else:
			self.x /= other
			self.y /= other
			self.z /= other
		
		return self	
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def Len( self ):
		return sqrt( self.x * self.x + self.y * self.y + self.z * self.z )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def Normalize( self ):
		len = self.Len()
		
		if ( len != 0 ):
			self.x /= len
			self.y /= len
			self.z /= len
			
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def MakeZero( self ):
		self.x = 0
		self.y = 0
		self.z = 0
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __str__( self ):
		return "( " + str( self.x ) + "; " + str( self.y ) + "; " + str( self.z ) + " )"		