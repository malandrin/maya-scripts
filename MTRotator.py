#-----------------------------------------------------------------
#-- MTRotator
#-----------------------------------------------------------------
import maya.mel as mel
import maya.cmds as cmds
from MTVector import *
from MTUtils import *

#-------------------------------------------------------------
#--
#-------------------------------------------------------------
class MTRotatorObject:
	
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __init__( self, object ):
		self.Object = object
		
		# posiciones iniciales del objeto y del pivote
		self.ObjectPosition = MTUGetPosition( object )
		self.ObjectRotation = MTUGetRotation( object )		
		self.PivotPosition  = MTUGetRotatePivotPosition( object )
		self.RotateAround   = None
				
		# nos quedamos con el orden de rotacion
		self.RotateOrder = cmds.xform( object, query = True, rotateOrder = True )
		
		# lista de rotaciones
		self.RotationList = [ ]
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def StartRotation( self, rotateAround ):
		self.ObjectPosition = MTUGetPosition( self.Object )
		self.ObjectRotation = MTUGetRotation( self.Object )		
		self.PivotPosition  = MTUGetRotatePivotPosition( self.Object )	
		cmds.xform( self.Object, pivots = ( rotateAround.x, rotateAround.y, rotateAround.z ), worldSpace = True )
		self.RotateAround = rotateAround

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def Rotate( self, rotation ):
		self.RotationList.append( rotation )

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------		
	def EndRotation( self ):
		numRotations  = len( self.RotationList )
		finalPivotPos = self.PivotPosition - self.RotateAround
		finalRotation = MTUGetRotation( self.Object )
		
		# ...
		cmds.makeIdentity( self.Object, translate = True, rotate = True )
		#cmds.xform( self.Object, centerPivots = True )
		
		# se rota el pivote para calcular la posicion final
		for i in range( 0, numRotations ):
			# rotaciones posibles: xyz | yzx | zxy | xzy | yxz | zyx
			if ( self.RotateOrder == "xyz" ):
				finalPivotPos = MTUXRotate( finalPivotPos, self.RotationList[ i ].x )
				finalPivotPos = MTUYRotate( finalPivotPos, self.RotationList[ i ].y )
				finalPivotPos = MTUZRotate( finalPivotPos, self.RotationList[ i ].z )
				
		# posicion final
		finalPivotPos = finalPivotPos + self.RotateAround
		finalPosition = self.ObjectPosition + ( finalPivotPos - self.PivotPosition )
				
		# movemos el objeto, colocamos el pivote en su posicion final y rotamos sobre el
		cmds.move( finalPosition.x, finalPosition.y, finalPosition.z, self.Object, relative = True )
		cmds.xform( self.Object, pivots = ( finalPivotPos.x, finalPivotPos.y, finalPivotPos.z ), worldSpace = True )
		cmds.xform( self.Object, rotation = ( finalRotation.x, finalRotation.y, finalRotation.z ), relative = True )
	
		# ...
		self.RotationList = [ ]
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def Reset( self ):
		MTUSetPosition( self.Object, self.ObjectPosition )
		MTUSetRotation( self.Object, self.ObjectRotation )
		MTUSetRotatePivotPosition( self.Object, self.PivotPosition )	
		
#-------------------------------------------------------------
#--
#-------------------------------------------------------------
class MTRotator:
	# ...
	PLUGIN_VERSION  = "1.0"
	WINDOW_NAME	    = "MTRotator"
	WINDOW_WIDTH    = 330
	WINDOW_HEIGHT   = 200
	
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __init__( self ):
		self.ButtonIsStart 				= False
		self.ObjectPicked				= None
		self.RotatePosition		    	= MTVector( 0.0, 0.0, 0.0 ) 
		self.RotateAroundSelected 		= -1
		self.SelectedObjects        	= None
		self.ObjectsToRotate        	= None
		self.IgnoreSelectionChangeEvent	= False
		self.CloseButtonPressed 		= False	
		self.DummyNode					= None
		self.CurrentContext				= None
		
		self.BuildUI()
		self.OnRotateAroundCenterBBoxSelected( None )
		self.OnSelectionChange()
		
		self.SelectionJob = cmds.scriptJob( event = ( "SelectionChanged", self.OnSelectionChange ), parent = self.Window )
		self.DeleteJob    = cmds.scriptJob( uiDeleted = ( self.Window, self.OnWindowClosed ) )
		
		# se crea un nodo invisible que servira para obtener las rotaciones de mundo
		self.DummyNode = cmds.createNode( "transform", skipSelect = True )		
		
		# nuevo rotator para saber cuando se termina de girar
		self.CurrentContext = cmds.currentCtx()
		self.ManipRotate = cmds.manipRotateContext( mode = 1, postDragCommand = ( self.OnObjectRotated, "transform" ) )	

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def OnObjectRotated( self ):
		# rotacion del nodo dummy
		rotation = MTUGetRotation( self.DummyNode )
		cmds.makeIdentity( self.DummyNode, rotate = True );
			
		# se gira el pivote segun la diferencia angular
		for i in range( 0, len( self.ObjectsToRotate ) ):
			if ( self.ObjectsToRotate[ i ] != self.DummyNode ):
				self.ObjectsToRotate[ i ].Rotate( rotation )		
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def OnSelectionChange( self ):
		if ( not self.IgnoreSelectionChangeEvent ):
			if ( not self.ButtonIsStart ): # se cancela lo que se estaba rotando 
				self.EndRotation( True, False )
				
			# ...
			self.SelectedObjects = [ ]
			self.SelectedObjects = mel.eval( "ls -sl" )
			objectsSelected = ( ( self.SelectedObjects is not None ) and len( self.SelectedObjects ) > 0 )
		
			if ( self.RotateAroundSelected == 1 ): # se quiere rotar sobre un objecto, si solo hay un nodo seleccionado, se activa el boton de pick
				cmds.button( self.bPickObjectToRotateAround, edit = True, enable = ( ( self.SelectedObjects is not None ) and ( len( self.SelectedObjects ) == 1 ) ) )
		
			self.UpdateRotateInfo()
		
			# se mira si se puede empezar la rotacion
			if ( self.RotateAroundSelected == 0 ): # centro del bounding box. Se necesita uno o mas objetos seleccionados para poder rotar
				self.SetStartButtonState( True, objectsSelected )
			elif ( self.RotateAroundSelected == 1 ): # se gira sobre la posicion de un objeto. Tiene que haber un valor valido
				self.SetStartButtonState( True, objectsSelected and ( self.ObjectPicked is not None ) )
			elif ( self.RotateAroundSelected == 2 ): # sobre una posicion xyz
				self.SetStartButtonState( True, objectsSelected )
		else:
			self.IgnoreSelectionChangeEvent = False
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def OnWindowClosed( self ):
		if ( not self.CloseButtonPressed ):
			self.EndRotation( True, True )
			
		cmds.delete( self.DummyNode )					
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def OnStartRotate( self, *args ):
		if ( self.ButtonIsStart ):
			self.ObjectsToRotate = [ ]
			
			cmds.makeIdentity( self.DummyNode, rotate = True );
		
			# nos quedamos con los objetos seleccionados		
			if ( self.SelectedObjects is not None ):
				for i in range( 0, len( self.SelectedObjects ) ):
					newObject = MTRotatorObject( self.SelectedObjects[ i ] )
				
					# se lleva el pivote a la posicion origen de rotacion
					newObject.StartRotation( self.RotatePosition )
					self.ObjectsToRotate.append( newObject )

				# se addea el nodo dummy a la lista de seleccionados
				MTUSetPosition( self.DummyNode, self.RotatePosition )
				self.IgnoreSelectionChangeEvent = True
				cmds.select( self.DummyNode, add = True )
				cmds.setToolTo( self.ManipRotate )
			
				# ..
				self.SetStartButtonState( False, True )
		else: # stop
			self.EndRotation( False, False )
			
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def EndRotation( self, cancel, destroying ):
		if ( self.CurrentContext != None ):
			cmds.setToolTo( self.CurrentContext )

		# ...
		if ( self.ObjectsToRotate is not None ):
			for i in range( 0, len( self.ObjectsToRotate ) ):
				if ( cancel ):
					self.ObjectsToRotate[ i ].Reset()
				else:
					self.ObjectsToRotate[ i ].EndRotation()
				
		# si el nodo dummy esta en la lista de seleccionados de maya, se saca
		if ( not destroying ):
			if ( self.DummyNode != None ):
				cmds.select( self.DummyNode, deselect = True )
				
			self.SetStartButtonState( True, True )		
			self.ObjectsToRotate = []
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def OnClose( self, *args ):
		if ( self.ButtonIsStart ):
			self.CloseButtonPressed = True
			cmds.deleteUI( self.Window )
		else: # cancelar la accion
			self.EndRotation( True, False )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def OnRotateAroundCenterBBoxSelected( self, *args ):
		cmds.button( self.bPickObjectToRotateAround, edit = True, enable = False )
		cmds.textField( self.txtRAPX, edit = True, enable = False )
		cmds.textField( self.txtRAPY, edit = True, enable = False )
		cmds.textField( self.txtRAPZ, edit = True, enable = False )
		
		# ...
		self.RotateAroundSelected = 0
		self.OnSelectionChange()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def OnRotateAroundObjectSelected( self, *args ):
		cmds.button( self.bPickObjectToRotateAround, edit = True, enable = ( self.SelectedObjects is not None ) and ( len( self.SelectedObjects ) == 1 ) )
		cmds.textField( self.txtRAPX, edit = True, enable = False )
		cmds.textField( self.txtRAPY, edit = True, enable = False )
		cmds.textField( self.txtRAPZ, edit = True, enable = False )
		
		# ...
		self.RotateAroundSelected = 1
		self.OnSelectionChange()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def OnRotateAroundPositionSelected( self, *args ):
		cmds.button( self.bPickObjectToRotateAround, edit = True, enable = False )
		cmds.textField( self.txtRAPX, edit = True, enable = True )
		cmds.textField( self.txtRAPY, edit = True, enable = True )
		cmds.textField( self.txtRAPZ, edit = True, enable = True )

		# ...
		self.RotateAroundSelected = 2
		self.OnSelectionChange()

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def OnPickObject( self, *args ):
		self.ObjectPicked = None
		
		if ( ( self.SelectedObjects is not None ) and ( len( self.SelectedObjects ) == 1 ) ):		
			self.ObjectPicked   = self.SelectedObjects[ 0 ]
			
		self.UpdateRotateInfo()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SetStartButtonState( self, start, enabled ):	
		self.ButtonIsStart = start
		buttonCaption 	   = "Start"
		closeCaption	   = "Close"
		
		if ( not start ):
			buttonCaption = "Apply"
			closeCaption  = "Cancel"
			
		cmds.button( self.bStartRotate, edit = True, label = buttonCaption, enable = enabled )
		cmds.button( self.bClose, edit = True, label = closeCaption )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def UpdateRotateInfo( self ):
		objectsToRotate	= ""
		objectsSelected = False
		
		if ( self.SelectedObjects is not None ):
			numSelectedObjects  = len( self.SelectedObjects )
			objectsSelected     = ( numSelectedObjects > 0 )
			objectsToRotate 	= str( numSelectedObjects ) + " = ( "
			
			# ...
			for i in range( 0, numSelectedObjects ):
				objectsToRotate += self.SelectedObjects[ i ]
				if ( i < ( numSelectedObjects - 1 ) ):
					objectsToRotate += ", "
					
			objectsToRotate += " )"
		else:
			objectsToRotate = "0 = ( None )"
		
		# ...
		cmds.text( self.txtObjectsToRotate, edit = True, label = "Objects to Rotate: " + objectsToRotate )
		
		rotateAround = "Rotate Around: "
		
		if ( self.RotateAroundSelected == 0 ): # centro del bounding box
			if ( self.SelectedObjects is not None ):
				self.RotatePosition.MakeZero()
				numObjects = len( self.SelectedObjects )
				if ( numObjects > 0 ):
					for i in range( 0, numObjects ):
						self.RotatePosition = self.RotatePosition + MTUGetRotatePivotPosition( self.SelectedObjects[ i ] );
					
					self.RotatePosition = self.RotatePosition / numObjects;		
				rotateAround += "( " + str( self.RotatePosition.x ) + "; " + str( self.RotatePosition.y ) + "; " + str( self.RotatePosition.z ) + " )"
			else:
				rotateAround += "None"
		elif ( self.RotateAroundSelected == 1 ): # se gira sobre la posicion de un objeto. Tiene que haber un valor valido
			if ( self.ObjectPicked is not None ):
				self.RotatePosition = MTUGetRotatePivotPosition( self.ObjectPicked )
				rotateAround += self.ObjectPicked
			else:
				rotateAround += "None"
		elif ( self.RotateAroundSelected == 2 ): # sobre una posicion xyz
			self.RotatePosition.x = cmds.textField( self.txtRAPX, query = True, text = True )
			self.RotatePosition.y = cmds.textField( self.txtRAPY, query = True, text = True )
			self.RotatePosition.z = cmds.textField( self.txtRAPZ, query = True, text = True )
			
			rotateAround += "( " + str( self.RotatePosition.x ) + "; " + str( self.RotatePosition.y ) + "; " + str( self.RotatePosition.z ) + " )"
					
		cmds.text( self.txtRotationPivot, edit = True, label = rotateAround )

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------			
	def	OnTextFieldValueChange( self, *args ):
		self.UpdateRotateInfo()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------			
	def BuildUI( self ):
		self.Window = cmds.window( title = self.WINDOW_NAME + " " + self.PLUGIN_VERSION, sizeable = True, resizeToFitChildren = True, widthHeight = ( 1, 1 ) )
		
		HalfWidth = ( self.WINDOW_WIDTH / 2 )
		
		# main column
		cmds.columnLayout()
		
		# rotate around layout
		cmds.radioCollection()		
		cmds.frameLayout( label = "Rotate Around", collapsable = False, width = self.WINDOW_WIDTH )
		cmds.columnLayout()
		cmds.rowColumnLayout( numberOfColumns = 1, columnWidth = [ ( 1, self.WINDOW_WIDTH ) ] )
		self.rbRotateAroundCenterBB = cmds.radioButton( label = "Center of objects", onCommand = self.OnRotateAroundCenterBBoxSelected, select = True )
		cmds.setParent( ".." ) #rowColumnLayout
		
		cmds.rowColumnLayout( numberOfColumns = 2, columnWidth = [ ( 1, HalfWidth ), ( 2, HalfWidth - 5 ) ] )
		self.rbRotateAroundObject = cmds.radioButton( label = "Object Pivot", onCommand = self.OnRotateAroundObjectSelected )
		self.bPickObjectToRotateAround = cmds.button( label = "Pick", command = self.OnPickObject )
		cmds.setParent( ".." ) #rowColumnLayout
		
		cmds.rowColumnLayout( numberOfColumns = 2, columnWidth = [ ( 1, HalfWidth ), ( 2, HalfWidth - 5 ) ] )
		self.rbRotateAroundPosition = cmds.radioButton( label = "Position (XYZ)", onCommand = self.OnRotateAroundPositionSelected )
		cmds.rowColumnLayout( numberOfColumns = 3, columnWidth = [ ( 1, ( HalfWidth / 3 ) - 1 ), ( 2, ( HalfWidth / 3 ) - 1 ), ( 3, ( HalfWidth / 3 ) - 1 ) ] )
		self.txtRAPX = cmds.textField( text = "0", changeCommand = self.OnTextFieldValueChange )
		self.txtRAPY = cmds.textField( text = "0", changeCommand = self.OnTextFieldValueChange )
		self.txtRAPZ = cmds.textField( text = "0", changeCommand = self.OnTextFieldValueChange )
		cmds.setParent( ".." ) #rowColumnLayout				
		cmds.setParent( ".." ) #rowColumnLayout		
		
		cmds.setParent( ".." ) #columnLayout
		cmds.setParent( ".." ) #frameLayout
		
		# info layout
		cmds.frameLayout( label = "Rotate Info", collapsable = False, width = self.WINDOW_WIDTH )
		cmds.columnLayout()
		self.txtObjectsToRotate = cmds.text( label = "Objects To Rotate: 0" )
		self.txtRotationPivot   = cmds.text( label = "Rotate around: none" )
		cmds.setParent( ".." ) #columnLayout
		cmds.setParent( ".." ) #frameLayout	
		
		# buttons layout
		cmds.rowColumnLayout( numberOfColumns = 2, columnWidth = [ ( 1, HalfWidth ), ( 2, HalfWidth ) ] )
		self.bStartRotate = cmds.button( label = "Start", command = self.OnStartRotate, enable = False )
		self.bClose = cmds.button( label = "Close", command = self.OnClose )
		cmds.setParent( ".." ) # rowColumnLayout		
		
		# ...
		cmds.showWindow( self.Window ) # main column
