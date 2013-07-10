#-------------------------------------------------------------
#-- Utils
#-------------------------------------------------------------
from MTVector import *
import maya.cmds as cmds
import maya.mel as mel

#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUGetPosition( object ):
	position = cmds.getAttr( "%s.translate" %object )
	return MTVector( position[ 0 ][ 0 ], position[ 0 ][ 1 ], position[ 0 ][ 2 ] )
	
#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUGetPositionInTime( object, time ):
	position = cmds.getAttr( "%s.translate" %object, time = time )
	return MTVector( position[ 0 ][ 0 ], position[ 0 ][ 1 ], position[ 0 ][ 2 ] )	
	
#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUSetPosition( object, position ):	
	cmds.setAttr( "%s.translate" %object, position.x, position.y, position.z )
	
#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUGetRotation( object ):
	rotation = cmds.getAttr( "%s.rotate" %object )
	return MTVector( rotation[ 0 ][ 0 ], rotation[ 0 ][ 1 ], rotation[ 0 ][ 2 ] )
	
#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUGetRotationInTime( object, time ):
	rotation = cmds.getAttr( "%s.rotate" %object, time = time )
	return MTVector( rotation[ 0 ][ 0 ], rotation[ 0 ][ 1 ], rotation[ 0 ][ 2 ] )	
	
#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUSetRotation( object, rotation ):	
	cmds.setAttr( "%s.rotate" %object, rotation.x, rotation.y, rotation.z )		
	
#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUGetScale( object ):
	scale = cmds.getAttr( "%s.scale" %object )
	return MTVector( scale[ 0 ][ 0 ], scale[ 0 ][ 1 ], scale[ 0 ][ 2 ] )
	
#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUSetScale( object, scale ):	
	cmds.setAttr( "%s.scale" %object, scale.x, scale.y, scale.z )
	
#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUSetTransform( object, position, rotation, scale ):
	MTUSetPosition( object, position )
	MTUSetRotation( object, rotation )
	MTUSetScale( object, scale )
	
#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUSetRotatePivotPosition( object, position ):
	cmds.move( position.x, position.y, position.z, "%s.rotatePivot" %object, relative = False )
	
#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUGetRotatePivotPosition( object ):
	pivotPosition = cmds.xform( object, query = True, rotatePivot = True, worldSpace = True )
	return MTVector( pivotPosition[ 0 ], pivotPosition[ 1 ], pivotPosition[ 2 ] )
	
#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUGetBoundingBox( object ):
	boundingBox = cmds.xform( object, query = True, objectSpace = True, boundingBox = True )
		
	minimum = MTVector( boundingBox[ 0 ], boundingBox[ 1 ], boundingBox[ 2 ] )
	maximum = MTVector( boundingBox[ 3 ], boundingBox[ 4 ], boundingBox[ 5 ] )
	center  = ( ( maximum + minimum ) / 2 )
	
	return [ minimum, maximum, center ]
	
#-------------------------------------------------------------
#--
#-------------------------------------------------------------		
def MTUXRotate( pos, angle ):
	Deg = mel.eval( "deg_to_rad( %f );" %angle )
	Rot = mel.eval( "rot " + ( "<< %f, %f, %f >>" %( pos.x, pos.y, pos.z ) ) + ( " << 1, 0, 0 >> %f" %Deg ) + ";" )
	return MTVector( Rot[ 0 ], Rot[ 1 ], Rot[ 2 ] )
		
#-------------------------------------------------------------
#--
#-------------------------------------------------------------		
def MTUYRotate( pos, angle ):
	Deg = mel.eval( "deg_to_rad( %f );" %angle )
	Rot = mel.eval( "rot " + ( "<< %f, %f, %f >>" %( pos.x, pos.y, pos.z ) ) + ( " << 0, 1, 0 >> %f" %Deg ) + ";" )
	return MTVector( Rot[ 0 ], Rot[ 1 ], Rot[ 2 ] )
		
#-------------------------------------------------------------
#--
#-------------------------------------------------------------		
def MTUZRotate( pos, angle ):
	Deg = mel.eval( "deg_to_rad( %f );" %angle )
	Rot = mel.eval( "rot " + ( "<< %f, %f, %f >>" %( pos.x, pos.y, pos.z ) ) + ( " << 0, 0, 1 >> %f" %Deg ) + ";" )
	return MTVector( Rot[ 0 ], Rot[ 1 ], Rot[ 2 ] )	