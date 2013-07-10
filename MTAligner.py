#-------------------------------------------------------------
#-- MTAligner
#-------------------------------------------------------------
import maya.mel as mel
import maya.cmds as cmds
from MTVector import *
from MTUtils import *

#-------------------------------------------------------------
#-- objects
#-------------------------------------------------------------
class MTAlignerObject:

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __init__( self, object ):
		self.Object = object
		self.CatchTranformValues()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def CatchTranformValues( self ):
		self.InitialPosition 		= MTUGetPosition( self.Object )
		self.InitialRotation 		= MTUGetRotation( self.Object )
		self.InitialScale    		= MTUGetScale( self.Object )
		self.InitialPivotPosition 	= MTUGetRotatePivotPosition( self.Object )
		self.InitialBoundingBox     = MTUGetBoundingBox( self.Object )		

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def AlignPivot( self, target, alignPosition ):
		targetPivot  = target.GetPivotPosition()
		
		if ( alignPosition[ 0 ] is False ):
			targetPivot.x = self.InitialPivotPosition.x
		if ( alignPosition[ 1 ] is False ):
			targetPivot.y = self.InitialPivotPosition.y
		if ( alignPosition[ 2 ] is False ):
			targetPivot.z = self.InitialPivotPosition.z
			
		MTUSetRotatePivotPosition( self.Object, targetPivot )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def AlignObject( self, target, alignPosition, alignRotation, alignScale, alignCurrent, alignTarget ):
		# se calcula la posicion destino en mundo a la posicion relativa al eje de coordenadas del objeto
		currentCenter    = self.GetWorldPosition() # el centro del BB
		targetCenter	 = target.GetWorldPosition() # el centro del BB
		currentWorldPos  = currentCenter.Clone()
		targetWorldPos   = targetCenter.Clone()
				
		# current
		if ( alignCurrent == 1 ): # Minimun
			currentWorldPos = self.GetMinimunBBox()
		elif ( alignCurrent == 3 ): # Pivot
			currentWorldPos = self.GetPivotPosition()
		elif ( alignCurrent == 4 ): # Maximun
			currentWorldPos = self.GetMaximunBBox()
			
		# target
		if ( alignTarget == 1 ): # Minimun
			targetWorldPos = target.GetMinimunBBox()
		elif ( alignTarget == 3 ): # Pivot
			targetWorldPos = target.GetPivotPosition()
		elif ( alignTarget == 4 ): # Maximun
			targetWorldPos = target.GetMaximunBBox()

		# offset relativo al centro
		currentOffset = ( currentWorldPos - currentCenter )
				
		# alineamos posicion
		finalPosition = ( ( targetWorldPos - currentOffset ) - ( currentCenter - self.GetPosition() ) ) # currentCenter - GetPosition() = cuando el objeto tiene el 0,0,0 reseteado su posicion, con esto se sacan las coordenadas de mundo
		
		if ( alignPosition[ 0 ] is False ):
			finalPosition.x = self.InitialPosition.x
		if ( alignPosition[ 1 ] is False ):
			finalPosition.y = self.InitialPosition.y
		if ( alignPosition[ 2 ] is False ):
			finalPosition.z = self.InitialPosition.z
			
		# rotacion
		finalRotation = target.GetRotation()
		
		if ( alignRotation[ 0 ] is False ):
			finalRotation.x = self.InitialRotation.x
		if ( alignRotation[ 1 ] is False ):
			finalRotation.y = self.InitialRotation.y
		if ( alignRotation[ 2 ] is False ):
			finalRotation.z = self.InitialRotation.z
			
		# escalado
		finalScale = target.GetScale()
		
		if ( alignScale[ 0 ] is False ):
			finalScale.x = self.InitialScale.x
		if ( alignScale[ 1 ] is False ):
			finalScale.y = self.InitialScale.y
		if ( alignScale[ 2 ] is False ):
			finalScale.z = self.InitialScale.z
		
		# aplicamos
		MTUSetTransform( self.Object, finalPosition, finalRotation, finalScale )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetPivotPosition( self ):
		return self.InitialPivotPosition.Clone()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetMinimunBBox( self ):
		return self.InitialBoundingBox[ 0 ].Clone()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetMaximunBBox( self ):
		return self.InitialBoundingBox[ 1 ].Clone()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetWorldPosition( self ):
		return self.InitialBoundingBox[ 2 ].Clone()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetPosition( self ):
		return self.InitialPosition.Clone()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetRotation( self ):
		return self.InitialRotation.Clone()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetScale( self ):
		return self.InitialScale.Clone()		
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def Reset( self ):
		MTUSetTransform( self.Object, self.InitialPosition, self.InitialRotation, self.InitialScale )
		MTUSetRotatePivotPosition( self.Object, self.InitialPivotPosition )
		

#-------------------------------------------------------------
#-- main class
#-------------------------------------------------------------
class MTAligner:

	# defines
	PLUGIN_VERSION  = "1.0"
	WINDOW_NAME	    = "MTAligner"
	WINDOW_WIDTH    = 330
	WINDOW_HEIGHT   = 200

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __init__( self ):
		self.RevertApply = False
		self.Current = None
		self.Target  = None
		
		self.BuildUI()
		self.EnableDisableControlsByApplyTo()
		self.OnSelectionChange()
		
		self.SelectionJob = cmds.scriptJob( event = ( "SelectionChanged", self.OnSelectionChange ), parent = self.Window )
		self.DeleteJob    = cmds.scriptJob( uiDeleted = ( self.Window, self.OnWindowClosed ) )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def ApplyAlign( self ):
		# transform
		cbPosX = cmds.checkBox( self.cbXPosition, query = True, value = True )
		cbPosY = cmds.checkBox( self.cbYPosition, query = True, value = True )
		cbPosZ = cmds.checkBox( self.cbZPosition, query = True, value = True )
		cbRotX = cmds.checkBox( self.cbXRotation, query = True, value = True )
		cbRotY = cmds.checkBox( self.cbYRotation, query = True, value = True )
		cbRotZ = cmds.checkBox( self.cbZRotation, query = True, value = True )
		cbScaX = cmds.checkBox( self.cbXScale, query = True, value = True )
		cbScaY = cmds.checkBox( self.cbYScale, query = True, value = True )
		cbScaZ = cmds.checkBox( self.cbZScale, query = True, value = True )
		
		# current-target
		rbCurrent = cmds.radioButtonGrp( self.rbCurrentObject, query = True, select = 1 )
		rbTarget  = cmds.radioButtonGrp( self.rbTargetObject, query = True, select = 1 )
		
		# align flags
		alignPosition = [ cbPosX, cbPosY, cbPosZ ]
		alignRotation = [ cbRotX, cbRotY, cbRotZ ]
		alignScale    = [ cbScaX, cbScaY, cbScaZ ]
				
		# option
		rbApplyTo = cmds.radioButtonGrp( self.rbApplyTo, query = True, select = 1 )

		if ( rbApplyTo == 1 ): # align pivots
			self.Current.AlignPivot( self.Target, alignPosition )
		else: # align objects
			self.Current.AlignObject( self.Target, alignPosition, alignRotation, alignScale, rbCurrent, rbTarget )
			
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------			
	def OnSelectionChange( self ):
		# si ya habia objetos seleccionados se les coloca en su posicion inicial
		if ( self.Current is not None ):
			self.Current.Reset()
			
		self.RevertApply = False
		self.Current = None
		self.Target  = None
		
		SelectedObjects = mel.eval( "ls -sl" )
		
		if ( SelectedObjects is not None ):
			numObjects = len( SelectedObjects )		
			
			if ( numObjects == 2 ): # se necesitan exactamente 2 objetos
				self.RevertApply = True
				
				self.Current = MTAlignerObject( SelectedObjects[ 0 ] )
				self.Target  = MTAlignerObject( SelectedObjects[ 1 ] )
				
				self.ApplyAlign()
				
		# si no hay 2 objetos seleccionados se desactivan los botones
		if ( self.Current is not None ):
			self.EnableAllControls( True )
			self.EnableDisableControlsByApplyTo()
		else:
			self.EnableAllControls( False )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------			
	def OnWindowClosed( self ):
		if ( self.RevertApply and self.Current is not None ):
			self.Current.Reset()				
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------			
	def OnAlignAttributeChange( self, *args ):
		self.ApplyAlign()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------		
	def OnAlignPositionChange( self, *args ):
		self.ApplyAlign()

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------			
	def OnApplyToChange( self, *args ):
		self.Current.Reset()
		self.ApplyAlign()
		self.EnableDisableControlsByApplyTo();
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def OnApply( self, *args ):
		self.ApplyAlign()
		self.Current.CatchTranformValues()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def OnDone( self, *args ):
		self.ApplyAlign()
		self.RevertApply = False # para detectar cuando se cierra pulsando en el boton de la barra de titulo
		cmds.deleteUI( self.Window )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def OnCancel( self, *args ):
		if ( self.Current is not None ):
			self.Current.Reset()
		
		self.RevertApply = False # para detectar cuando se cierra pulsando en el boton de la barra de titulo
		cmds.deleteUI( self.Window )

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def ToggleAlignPositionCheckBoxesValues( self, *args ):
		XCheck = cmds.checkBox( self.cbXPosition, query = True, value = True )
		YCheck = cmds.checkBox( self.cbYPosition, query = True, value = True )
		ZCheck = cmds.checkBox( self.cbZPosition, query = True, value = True )

		cmds.checkBox( self.cbXPosition, edit = True, value = ( False if XCheck else True ) )
		cmds.checkBox( self.cbYPosition, edit = True, value = ( False if YCheck else True ) )
		cmds.checkBox( self.cbZPosition, edit = True, value = ( False if ZCheck else True ) )
		
		self.ApplyAlign()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def ToggleAlignOrientationCheckBoxesValues( self, *args ):
		XCheck = cmds.checkBox( self.cbXRotation, query = True, value = True )
		YCheck = cmds.checkBox( self.cbYRotation, query = True, value = True )
		ZCheck = cmds.checkBox( self.cbZRotation, query = True, value = True )

		cmds.checkBox( self.cbXRotation, edit = True, value = ( False if XCheck else True ) )
		cmds.checkBox( self.cbYRotation, edit = True, value = ( False if YCheck else True ) )
		cmds.checkBox( self.cbZRotation, edit = True, value = ( False if ZCheck else True ) )
		
		self.ApplyAlign()

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def ToggleMatchScaleCheckBoxesValues( self, *args ):
		XCheck = cmds.checkBox( self.cbXScale, query = True, value = True )
		YCheck = cmds.checkBox( self.cbYScale, query = True, value = True )
		ZCheck = cmds.checkBox( self.cbZScale, query = True, value = True )

		cmds.checkBox( self.cbXScale, edit = True, value = ( False if XCheck else True ) )
		cmds.checkBox( self.cbYScale, edit = True, value = ( False if YCheck else True ) )
		cmds.checkBox( self.cbZScale, edit = True, value = ( False if ZCheck else True ) )
		
		self.ApplyAlign()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def EnableAllControls( self, enabled ):
		cmds.checkBox( self.cbXPosition, edit = True, enable = enabled )
		cmds.checkBox( self.cbYPosition, edit = True, enable = enabled )
		cmds.checkBox( self.cbZPosition, edit = True, enable = enabled )

		cmds.checkBox( self.cbXRotation, edit = True, enable = enabled )
		cmds.checkBox( self.cbYRotation, edit = True, enable = enabled )
		cmds.checkBox( self.cbZRotation, edit = True, enable = enabled )
		
		cmds.checkBox( self.cbXScale, edit = True, enable = enabled )
		cmds.checkBox( self.cbYScale, edit = True, enable = enabled )
		cmds.checkBox( self.cbZScale, edit = True, enable = enabled )
		
		cmds.button( self.bTogglePosition, edit = True, enable = enabled )
		cmds.button( self.bToggleRotation, edit = True, enable = enabled )				
		cmds.button( self.bToggleScale, edit = True, enable = enabled )
		
		cmds.button( self.bApply, edit = True, enable = enabled )
		cmds.button( self.bDone, edit = True, enable = enabled )
		
		cmds.radioButtonGrp( self.rbApplyTo, edit = True, enable = enabled )
		
		cmds.radioButtonGrp( self.rbCurrentObject, edit = True, enable = enabled )
		cmds.radioButtonGrp( self.rbTargetObject, edit = True, enable = enabled )
		
		if ( enabled ):
			cmds.textField( self.tfCurrent, edit = True, text = self.Current.Object )
			cmds.textField( self.tfTarget, edit = True, text = self.Target.Object )
		else:
			cmds.textField( self.tfCurrent, edit = True, text = "None" )
			cmds.textField( self.tfTarget, edit = True, text = "None" )
			
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def EnableDisableControlsByApplyTo( self ):		
		rbApplyTo = cmds.radioButtonGrp( self.rbApplyTo, query = True, select = 1 )
		
		controlsEnable = ( rbApplyTo == 2 )
		
		cmds.checkBox( self.cbXRotation, edit = True, enable = controlsEnable )
		cmds.checkBox( self.cbYRotation, edit = True, enable = controlsEnable )
		cmds.checkBox( self.cbZRotation, edit = True, enable = controlsEnable )		
		
		cmds.checkBox( self.cbXScale, edit = True, enable = controlsEnable )
		cmds.checkBox( self.cbYScale, edit = True, enable = controlsEnable )
		cmds.checkBox( self.cbZScale, edit = True, enable = controlsEnable )
		
		cmds.button( self.bToggleScale, edit = True, enable = controlsEnable )
		
		cmds.radioButtonGrp( self.rbCurrentObject, edit = True, enable = controlsEnable )
		cmds.radioButtonGrp( self.rbTargetObject, edit = True, enable = controlsEnable )			
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------			
	def BuildUI( self ):
		self.Window = cmds.window( title = self.WINDOW_NAME + " " + self.PLUGIN_VERSION, sizeable = True, resizeToFitChildren = True, widthHeight = ( self.WINDOW_WIDTH, self.WINDOW_HEIGHT ) )
		
		HalfWidth = ( self.WINDOW_WIDTH / 2 )
		
		# main column
		cmds.columnLayout()
		
		# select info layout
		cmds.frameLayout( label = "Selection Info", collapsable = False, width = self.WINDOW_WIDTH )
		cmds.columnLayout()
		cmds.rowColumnLayout( numberOfColumns = 2 )
		cmds.text( label = "Current:" )
		self.tfCurrent = cmds.textField( editable = False, text = "None" )
		cmds.text( label = "Target:" )
		self.tfTarget = cmds.textField( editable = False, text = "None" )		
		
		cmds.setParent( ".." ) # rowColumnLayout
		cmds.setParent( ".." ) # columnLayout
		cmds.setParent( ".." ) # frameLayout				
		
		# position layout
		cmds.frameLayout( label = "Align Position (World)", collapsable = False, width = self.WINDOW_WIDTH )
		cmds.columnLayout()
		cmds.rowColumnLayout( numberOfColumns = 3, columnWidth = [ ( 1, self.WINDOW_WIDTH / 3 ), ( 2, self.WINDOW_WIDTH / 3 ), ( 3, self.WINDOW_WIDTH / 3 ) ] )
		self.cbXPosition   = cmds.checkBox( label = "X Position", value = True, changeCommand = self.OnAlignAttributeChange )
		self.cbYPosition   = cmds.checkBox( label = "Y Position", value = True, changeCommand = self.OnAlignAttributeChange )
		self.cbZPosition   = cmds.checkBox( label = "Z Position", value = True, changeCommand = self.OnAlignAttributeChange )
		cmds.setParent( ".." ) # rowColumnLayout
		self.bTogglePosition = cmds.button( label = "Toggle Values", command = self.ToggleAlignPositionCheckBoxesValues )
		
		# custom-target options		
		cmds.rowColumnLayout( numberOfColumns = 2, columnWidth = [ ( 1, HalfWidth - 2 ), ( 2, HalfWidth - 2 ) ] )
		
		cmds.frameLayout( label = "Current Object:", width = HalfWidth )
		self.rbCurrentObject = cmds.radioButtonGrp( onCommand = self.OnAlignPositionChange, vertical = True, select = 3, numberOfRadioButtons = 4, labelArray4 = [ "Minimun", "Center", "Pivot Center", "Maximun" ] )
		cmds.setParent( ".." ) # frameLayout

		cmds.frameLayout( label = "Target Object:", width = HalfWidth )
		self.rbTargetObject = cmds.radioButtonGrp( onCommand = self.OnAlignPositionChange, vertical = True, select = 3, numberOfRadioButtons = 4, labelArray4 = [ "Minimun", "Center", "Pivot Center", "Maximun" ] )
		cmds.setParent( ".." ) # frameLayout
		
		cmds.setParent( ".." ) # rowColumnLayout					
		cmds.setParent( ".." ) # columnLayout
		cmds.setParent( ".." ) # frameLayout
		
		# rotation layout
		cmds.frameLayout( label = "Align Orientation (Local)", collapsable = False, width = self.WINDOW_WIDTH )
		cmds.columnLayout()
		cmds.rowColumnLayout( numberOfColumns = 3, columnWidth = [ ( 1, self.WINDOW_WIDTH / 3 ), ( 2, self.WINDOW_WIDTH / 3 ), ( 3, self.WINDOW_WIDTH / 3 ) ] )
		self.cbXRotation = cmds.checkBox( label = "X Axis", value = True, changeCommand = self.OnAlignAttributeChange )
		self.cbYRotation = cmds.checkBox( label = "Y Axis", value = True, changeCommand = self.OnAlignAttributeChange )
		self.cbZRotation = cmds.checkBox( label = "Z Axis", value = True, changeCommand = self.OnAlignAttributeChange )
		cmds.setParent( ".." ) # rowColumnLayout
		self.bToggleRotation = cmds.button( label = "Toggle Values", command = self.ToggleAlignOrientationCheckBoxesValues )		
		cmds.setParent( ".." ) # columnLayout
		cmds.setParent( ".." ) # frameLayout		
		
		# scale layout
		cmds.frameLayout( label = "Match Scale", collapsable = False, width = self.WINDOW_WIDTH )
		cmds.columnLayout()
		cmds.rowColumnLayout( numberOfColumns = 3, columnWidth = [ ( 1, self.WINDOW_WIDTH / 3 ), ( 2, self.WINDOW_WIDTH / 3 ), ( 3, self.WINDOW_WIDTH / 3 ) ] )
		self.cbXScale = cmds.checkBox( label = "X Axis", value = False, changeCommand = self.OnAlignAttributeChange )
		self.cbYScale = cmds.checkBox( label = "Y Axis", value = False, changeCommand = self.OnAlignAttributeChange )
		self.cbZScale = cmds.checkBox( label = "Z Axis", value = False, changeCommand = self.OnAlignAttributeChange )
		cmds.setParent( ".." ) # rowColumnLayout
		self.bToggleScale = cmds.button( label = "Toggle Values", command = self.ToggleMatchScaleCheckBoxesValues )					
		cmds.setParent( ".." ) # columnLayout
		cmds.setParent( ".." ) # frameLayout			
		
		# apply to layout
		cmds.frameLayout( label = "Apply To", collapsable = False, width = self.WINDOW_WIDTH )
		self.rbApplyTo = cmds.radioButtonGrp( select = 2, onCommand = self.OnApplyToChange, numberOfRadioButtons = 2, labelArray2 = [ "Pivot", "Object" ] )
		cmds.setParent( ".." ) # frameLayout
		
		# buttons layout
		cmds.rowColumnLayout( numberOfColumns = 3, columnWidth = [ ( 1, self.WINDOW_WIDTH / 3 ), ( 2, self.WINDOW_WIDTH / 3 ), ( 3, self.WINDOW_WIDTH / 3 ) ] )
		self.bApply = cmds.button( label = "Apply", command = self.OnApply )
		self.bDone  = cmds.button( label = "Done", command = self.OnDone )
		cmds.button( label = "Cancel", command = self.OnCancel )				
		cmds.setParent( ".." ) # rowColumnLayout
		
		# ...
		cmds.showWindow( self.Window ) # main column
		