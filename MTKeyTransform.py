#-------------------------------------------------------------
#-- MTKeyTransform
#-------------------------------------------------------------
from MTVector import *
from MTUtils import *
import maya.mel as mel
import maya.cmds as cmds

#-------------------------------------------------------------
#-- main class
#-------------------------------------------------------------
class MTKeyTransform:

	# defines
	PLUGIN_VERSION  = "1.0"
	WINDOW_NAME	    = "MTKeyTransform"
	WINDOW_WIDTH    = 190
	WINDOW_HEIGHT   = 200
	
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __init__( self ):
		self.ReferenceFrame	= 0
		self.StartFrame     = 1
		self.EndFrame		= 200
		self.NodesSelected  = None
		
		self.BuildUI()
		self.OnSelectionChange()
		
		self.SelectionJob = cmds.scriptJob( event = ( "SelectionChanged", self.OnSelectionChange ), parent = self.Window )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------			
	def OnSelectionChange( self ):		
		self.NodesSelected = mel.eval( "ls -sl" )
		
		isValid = ( ( self.NodesSelected != None ) and ( len( self.NodesSelected ) > 0 ) )
		cmds.button( self.bTransform, edit = True, enable = isValid )
		
		nodesList = "None"
		
		if ( isValid ):
			nodesList 	 = ""
			insertReturn = False
			numNodes     = len( self.NodesSelected )
			
			for i in range( 0, numNodes ):
				nodesList += self.NodesSelected[ i ]
				
				if ( i < numNodes - 1 ):
					if ( insertReturn ):
						nodesList += ",\n"
						insertReturn = False
					else:
						nodesList += ", "
						insertReturn = True
		
		cmds.text( self.txtNodesSelected, edit = True, label = nodesList )
			
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def MoveNode( self, node, startFrame, endFrame, offset ):
		nodeAttributes = [ ".translateX", ".translateY", ".translateZ" ]
		nodeValues	   = [ offset.x, offset.y, offset.z ]

		for i in range( 0, 3 ):
			nodeAttr = node + nodeAttributes[ i ]
			keys 	 = cmds.keyframe( nodeAttr, time = ( startFrame, endFrame ), query = True, timeChange = True )
			
			if ( keys != None ): # puede no existir el atributo en el nodo
				for key in keys:
					self.SetKeyValue( nodeAttr, key, self.GetKeyValue( nodeAttr, key ) + nodeValues[ i ] )
				
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def RotateNode( self, node, startFrame, endFrame, offset ):
		nodeAttributes = [ ".rotateX", ".rotateY", ".rotateZ" ]
		nodeValues	   = [ offset.x, offset.y, offset.z ]

		for i in range( 0, 3 ):
			nodeAttr = node + nodeAttributes[ i ]
			keys 	 = cmds.keyframe( nodeAttr, time = ( startFrame, endFrame ), query = True, timeChange = True )
			
			if ( keys != None ): # puede no existir el atributo en el nodo
				for key in keys:
					self.SetKeyValue( nodeAttr, key, self.GetKeyValue( nodeAttr, key ) + nodeValues[ i ] )				
			
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetKeyValue( self, node, frame ):
		return cmds.keyframe( node, time = ( frame, frame ), query = True, valueChange = True )[ 0 ]
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SetKeyValue( self, node, frame, value ):
		cmds.keyframe( node, time = ( frame, frame ), valueChange = value )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def OnTransform( self, *args ):	
		for node in self.NodesSelected:
			refPosition   = MTUGetPositionInTime( node, self.ReferenceFrame )
			startPosition = MTUGetPositionInTime( node, self.StartFrame )
			refRotation   = MTUGetRotationInTime( node, self.ReferenceFrame )
			startRotation = MTUGetRotationInTime( node, self.StartFrame )
			
			self.MoveNode( node, self.StartFrame, self.EndFrame, refPosition - startPosition )
			self.RotateNode( node, self.StartFrame, self.EndFrame, refRotation - startRotation )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def OnClose( self, *args ):
		cmds.deleteUI( self.Window )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------			
	def	OnTextFieldValueChange( self, *args ):
		self.ReferenceFrame	= cmds.textField( self.txtReferenceFrame, query = True, text = True )
		self.StartFrame     = cmds.textField( self.txtStartFrame, query = True, text = True )
		self.EndFrame		= cmds.textField( self.txtEndFrame, query = True, text = True )	
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------			
	def BuildUI( self ):
		self.Window = cmds.window( title = self.WINDOW_NAME + " " + self.PLUGIN_VERSION, sizeable = True, resizeToFitChildren = True, widthHeight = ( self.WINDOW_WIDTH, self.WINDOW_HEIGHT ) )
		
		HalfWidth = ( self.WINDOW_WIDTH / 2 )

		# main column
		cmds.columnLayout()

		# 
		cmds.frameLayout( label = "Frames Info", collapsable = False, width = self.WINDOW_WIDTH )
		cmds.columnLayout()
		cmds.rowColumnLayout( numberOfColumns = 2, columnWidth = [ ( 1, 70 ), ( 2, self.WINDOW_WIDTH - 80 ) ] )
		cmds.text( label = "Start", align = "left" )
		self.txtStartFrame = cmds.textField( text = self.StartFrame, changeCommand = self.OnTextFieldValueChange )
		cmds.text( label = "End", align = "left" )
		self.txtEndFrame = cmds.textField( text = self.EndFrame, changeCommand = self.OnTextFieldValueChange )
		cmds.text( label = "Reference", align = "left" )
		self.txtReferenceFrame = cmds.textField( text = self.ReferenceFrame, changeCommand = self.OnTextFieldValueChange )
		cmds.setParent( ".." ) #rowColumnLayout		
		cmds.setParent( ".." ) # columnLayout
		cmds.setParent( ".." ) # frameLayout
		
		# 
		cmds.frameLayout( label = "Nodes Selected", collapsable = False, width = self.WINDOW_WIDTH )
		cmds.columnLayout()
		self.txtNodesSelected = cmds.text( label = "None", align = "left", recomputeSize = False, height = 100 )
		cmds.setParent( ".." ) #columnLayout		
		cmds.setParent( ".." ) # frameLayout
		
		# buttons layout		
		cmds.rowColumnLayout( numberOfColumns = 2, columnWidth = [ ( 1, HalfWidth ), ( 2, HalfWidth ) ] )
		self.bTransform = cmds.button( label = "Transform", command = self.OnTransform, enable = False )
		self.bClose = cmds.button( label = "Close", command = self.OnClose )
		cmds.setParent( ".." ) # rowColumnLayout		
		
		# ...
		cmds.showWindow( self.Window ) # main column		
