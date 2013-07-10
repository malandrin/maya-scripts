#-------------------------------------------------------------
#-- MTRuntimeKeyTransform
#-------------------------------------------------------------
from MTVector import *
import maya.mel as mel
import maya.cmds as cmds

#-------------------------------------------------------------
#-- Configuration
#-------------------------------------------------------------
Config_UseOnlyNodesInList = True  # si True, solo deja seleccionar los nodos que estan en la lista de abajo; si False muestra todos los nodos con keys

# Nombre del nodo; Sumar pivote a posicion
Config_Nodes = \
[ \
	( u"Torso_ctrl", 		True ),		\
	( u"Chest_ctrl", 		True ),		\
	( u"ik_L_Foot_ctrl", 	False ),	\
	( u"ik_R_Foot_ctrl", 	False ),	\
	( u"ik_L_Knee_ctrl", 	False ),	\
	( u"ik_R_Knee_ctrl", 	False ),	\
	( u"Jaw_ctrl", 			True ),		\
	( u"Pelvis_ctrl", 		True ),		\
	( u"ik_L_Weapon_ctrl", 	False ),	\
	( u"Head_ctrl", 		False )	 	\
]

#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUSetPosition( object, position ):	
	cmds.setAttr( "%s.translate" %object, position.x, position.y, position.z )

#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUGetPosition( object ):
	position = cmds.getAttr( "%s.translate" %object )
	return MTVector( position[ 0 ][ 0 ], position[ 0 ][ 1 ], position[ 0 ][ 2 ] )
	
#-------------------------------------------------------------
#--
#-------------------------------------------------------------
def MTUGetRotatePivotPosition( object ):
	pivotPosition = cmds.xform( object, query = True, rotatePivot = True, worldSpace = True )
	return MTVector( pivotPosition[ 0 ], pivotPosition[ 1 ], pivotPosition[ 2 ] )	

#-------------------------------------------------------------
#-- Frame Marker
#-------------------------------------------------------------
class FrameMarker:

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __init__( self, gizmo ):
		self.Gizmo 		= gizmo
		self.Position 	= MTVector( 0, 0, 0 )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SetPosition( self, position ):
		self.Position = position
		MTUSetPosition( self.Gizmo, position )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetPosition( self ):
		return self.Position
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetGizmo( self ):
		return self.Gizmo

#-------------------------------------------------------------
#-- Manip
#-------------------------------------------------------------
class Manip:
	
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __init__( self, gizmo ):
		self.Gizmo 		= gizmo
		self.Position 	= MTVector( 0, 0, 0 )
		self.TransXJob  = -1
		self.TransYJob  = -1
		self.TransZJob  = -1
		self.App		= None
		self.FrameInfo  = None
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetGizmo( self ):
		return self.Gizmo
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def CalcPosition( self ):
		self.Position = MTUGetPosition( self.Gizmo )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetPosition( self ):
		return self.Position
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SetApp( self, app ):
		self.App = app
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SetFrame( self, frame ):
		self.Frame = frame
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetFrame( self ):
		return self.Frame
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def CreateTranslationScriptJobs( self ):
		self.DestroyTranslationScriptJobs()
		
		self.TransXJob = cmds.scriptJob( attributeChange = ( self.Gizmo + ".translateX", self.App.OnTranslationManipChange ), parent = self.App.Window )
		self.TransYJob = cmds.scriptJob( attributeChange = ( self.Gizmo + ".translateY", self.App.OnTranslationManipChange ), parent = self.App.Window )
		self.TransZJob = cmds.scriptJob( attributeChange = ( self.Gizmo + ".translateZ", self.App.OnTranslationManipChange ), parent = self.App.Window )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def DestroyTranslationScriptJobs( self ):
		if ( self.TransXJob != -1 ):
			cmds.scriptJob( kill = self.TransXJob )
			self.TransXJob = -1
		
		if ( self.TransYJob != -1 ):
			cmds.scriptJob( kill = self.TransYJob )
			self.TransYJob = -1
			
		if ( self.TransZJob != -1 ):
			cmds.scriptJob( kill = self.TransZJob )
			self.TransZJob = -1


#-------------------------------------------------------------
#-- FrameInfo
#-------------------------------------------------------------
class FrameInfo:

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __init__( self, node, frame, pivotPosition ):
		self.Node					= node
		self.Frame					= frame
		self.PivotPosition          = [ pivotPosition.x, pivotPosition.y, pivotPosition.z ]
		self.HasTranslationKeysAxis = [ False, False, False ]
		self.HasTranslationKeys     = False
		self.TranslationManip       = None
		self.FrameMarker			= None
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SetTranslationKey( self, axis ):
		self.HasTranslationKeysAxis[ axis ] = True
		self.HasTranslationKeys = True
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def RemoveTranslationKey( self, axis ):
		self.HasTranslationKeysAxis[ axis ] = False
		self.HasTranslationKeys = ( self.HasTranslationKeysAxis[ 0 ] or self.HasTranslationKeysAxis[ 1 ] or self.HasTranslationKeysAxis[ 2 ] )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetPosition( self ):
		return MTVector( self.PivotPosition[ 0 ], self.PivotPosition[ 1 ], self.PivotPosition[ 2 ] )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SetPosition( self, position, offset ):
		self.PivotPosition[ 0 ] = position.x
		self.PivotPosition[ 1 ] = position.y
		self.PivotPosition[ 2 ] = position.z
					
		# ... si tiene manipulador se actualiza su posicion
		if ( self.TranslationManip != None ):		
			gizmoPos = MTVector( self.PivotPosition[ 0 ], self.PivotPosition[ 1 ], self.PivotPosition[ 2 ] ) + offset
			
			if ( not ( gizmoPos == MTUGetPosition( self.TranslationManip.GetGizmo() ) ) ):
				MTUSetPosition( self.TranslationManip.GetGizmo(), gizmoPos )
				
			self.TranslationManip.CalcPosition()
			
		# ... tiene marker? ...
		if ( self.FrameMarker != None ):
			gizmoPos = MTVector( self.PivotPosition[ 0 ], self.PivotPosition[ 1 ], self.PivotPosition[ 2 ] ) + offset
			self.FrameMarker.SetPosition( gizmoPos )

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def HasTranslationKey( self ):
		return self.HasTranslationKeys;
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def HasTranslationKeyAxis( self, axis ):
		return self.HasTranslationKeysAxis[ axis ];		
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SetTranslationManip( self, manip, offset ):
		self.TranslationManip = manip
		MTUSetPosition( self.TranslationManip.GetGizmo(), self.GetPosition() + offset )
		manip.CalcPosition()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SetFrameMarker( self, marker, offset ):
		self.FrameMarker = marker
		MTUSetPosition( self.FrameMarker.GetGizmo(), self.GetPosition() + offset )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetTranslationManipGizmo( self ):
		if ( self.TranslationManip != None ):
			return self.TranslationManip.GetGizmo()
			
		return None
				
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------		
	def OnTranslationManipMove( self, offset ):
		offsetValues = [ offset.x, offset.y, offset.z ]
		
		# ... se actualiza los valores de la key ...
		nodesAttr = [ ".translateX", ".translateY", ".translateZ" ]
		
		for i in range( 0, 3 ):					
			if ( self.HasTranslationKeysAxis[ i ] ):
				value = cmds.keyframe( self.Node + nodesAttr[ i ], time = ( self.Frame, self.Frame ), query = True, valueChange = True )[ 0 ]
				cmds.keyframe( self.Node + nodesAttr[ i ], time = ( self.Frame, self.Frame ), valueChange = value + offsetValues[ i ] )
				
#-------------------------------------------------------------
#-- SequenceInfo
#-------------------------------------------------------------
class SequenceInfo:

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __init__( self, node ):
		self.Node 	    		= node
		self.FramesInfo 		= [ ]
		self.NumTranslationKeys = -1
		self.PivotOffset		= MTVector( 0, 0, 0 )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def AddFrameInfo( self, frameInfo ):
		self.FramesInfo.append( frameInfo )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SetFramePosition( self, frame, position ):
		self.FramesInfo[ frame ].SetPosition( position, self.PivotOffset )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetFrameInfo( self, index ):
		return self.FramesInfo[ index ]
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetNode( self ):
		return self.Node
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SetTranslationKey( self, axis, frame ):
		self.FramesInfo[ frame ].SetTranslationKey( axis )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def FrameHasTranslationKey( self, frame ):
		return self.FramesInfo[ frame ].HasTranslationKey()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetFramePosition( self, frame ):
		return ( self.FramesInfo[ frame ].GetPosition() + self.PivotOffset )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SetFrameTranslationManip( self, frame, manip ):
		self.FramesInfo[ frame ].SetTranslationManip( manip, self.PivotOffset )
		manip.SetFrame( frame )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SetFrameMarker( self, frame, marker ):
		self.FramesInfo[ frame ].SetFrameMarker( marker, self.PivotOffset )

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------		
	def GetFrameWithTranslationManipGizmo( self, gizmo ):
		return next( ( frame for frame in self.FramesInfo if frame.GetTranslationManipGizmo() == gizmo ), None )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SetPivotOffset( self, offset ):
		self.PivotOffset = offset
			
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetNumTranslationKeys( self ):
		# ... se cachea el valor ...
		if ( self.NumTranslationKeys == -1 ):
			self.NumTranslationKeys = 0
			
			for frame in self.FramesInfo:
				if ( frame.HasTranslationKey ):
					self.NumTranslationKeys += 1
			
		return self.NumTranslationKeys

#-------------------------------------------------------------
#-- main class
#-------------------------------------------------------------
class MTRuntimeKeyTransform:

	# defines
	PLUGIN_VERSION  = "1.0"
	WINDOW_NAME	    = "MTRuntimeKeyTransform"
	WINDOW_WIDTH    = 200
	WINDOW_HEIGHT   = 300
	
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def __init__( self ):
		self.ActiveNode					= ""
		self.ActiveManip				= None
		self.StartFrame 				= 1
		self.EndFrame   				= 21
		self.Curve      				= None
		self.NodesWithKeys 				= self.GetNodesWithTranslationKeys( cmds.ls( visible = True, objectsOnly = True, transforms = True, geometry = True ) )
		self.SequenceInfo   			= [ ]
		self.TranslationManips 			= [ ]
		self.FrameMarkers				= [ ]
		self.SelectedNodes				= [ ]
		self.NumTranslationManipsUsed 	= 0
		self.NumFrameMarkersUsed		= 0
		
		self.BuildUI()
		self.ListNodesWithTranslationKeys()
		self.EnableNodesList( False )
		self.OnSelectionChange()
		
		# ...
		self.DeleteJob = cmds.scriptJob( uiDeleted = ( self.Window, self.OnWindowClosed ) )
		self.SelectionJob = cmds.scriptJob( event = ( "SelectionChanged", self.OnSelectionChange ), parent = self.Window )

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def SelectNode( self, node ):
		self.ActiveNode = node
		self.CreateCurve()
		self.ActivateTranslationManips()
		self.ActivateFrameMarkers()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def ActivateFrameMarkers( self ):
		self.ResetFrameMarkersUsed()
		
		sequence = next( ( seq for seq in self.SequenceInfo if seq.GetNode() == self.ActiveNode ), None )		
		numKeys  = sequence.GetNumTranslationKeys()
		
		# ...
		for f in range( self.StartFrame, self.EndFrame + 1 ):
			frame = ( f - self.StartFrame )
			
			if ( not sequence.FrameHasTranslationKey( frame ) ):
				marker = self.GetFrameMarker()
				sequence.SetFrameMarker( frame, marker )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def ActivateTranslationManips( self ):
		self.ResetTranslationManipsUsed()
		
		sequence = next( ( seq for seq in self.SequenceInfo if seq.GetNode() == self.ActiveNode ), None )		
		numKeys  = sequence.GetNumTranslationKeys()
		
		# ...
		for f in range( self.StartFrame, self.EndFrame + 1 ):
			frame = ( f - self.StartFrame )
			
			if ( sequence.FrameHasTranslationKey( frame ) == True ):
				manip = self.GetTranslationManip()
				sequence.SetFrameTranslationManip( frame, manip )
				manip.CreateTranslationScriptJobs()
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def CreateCurve( self ):
		sequence = next( ( seq for seq in self.SequenceInfo if seq.GetNode() == self.ActiveNode ), None )
		points   = [ ]
		
		for f in range( self.StartFrame, self.EndFrame + 1 ):
			vector = sequence.GetFramePosition( f - self.StartFrame )
			point  = vector.x, vector.y, vector.z
			
			points.append( point )
			
		if ( self.Curve == None ):
			self.Curve = cmds.curve( degree = 1, point = points )
		else:
			self.Curve = cmds.curve( self.Curve, replace = True, point = points )
			
		# ... si ya hay curva, ya podemos hacer un refresh ...
		cmds.button( self.bRefreshCurve, edit = True, enable = True )

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def AnalyzeSequence( self ):
		self.SequenceInfo = self.CalculateSequenceInfo()
		self.GetTranslateKeysInfo()

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetTranslateKeysInfo( self ):
		nodeAttributes = [ ".translateX", ".translateY", ".translateZ" ]
		
		# ... nodos ...
		for node in self.NodesWithKeys:
			sequence = next( ( seq for seq in self.SequenceInfo if seq.GetNode() == node ), None )
			
			# ... keys ...
			for i in range( 0, 3 ):
				nodeAttr = node + nodeAttributes[ i ]
				keys     = cmds.keyframe( nodeAttr, time = ( self.StartFrame, self.EndFrame ), query = True, timeChange = True )
								
				# ...
				if ( keys != None ):
					for key in keys:
						ikey = int( key )
						sequence.SetTranslationKey( i, ikey - self.StartFrame )

						
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def CalculateSequenceInfo( self ):
		sequenceInfo = [ ]
		
		# ...
		for i in range( self.StartFrame, self.EndFrame + 1 ):
			for node in self.NodesWithKeys:
				sequence = next( ( seq for seq in sequenceInfo if seq.GetNode() == node ), None )

				if ( sequence == None ):
					sequence = SequenceInfo( node )
					sequenceInfo.append( sequence )

				# ...
				newFrameInfo = FrameInfo( node, i, self.GetWorldPosition( node, i ) ) #MTUGetRotatePivotPosition( node ) )
				sequence.AddFrameInfo( newFrameInfo )

		# ... offset relativo al pivote ...
		currentTime = cmds.currentTime( query = True )
		cmds.currentTime( self.StartFrame )
		
		for node in self.NodesWithKeys:
			sequence = next( ( seq for seq in sequenceInfo if seq.GetNode() == node ), None )
			
			# ... si la secuencia es de un nodo con el eje reseteado, se le suma el pivote ...
			isReseted = False
			cfgNode   = next( ( n for n in Config_Nodes if n[ 0 ] == node ), None )

			if ( cfgNode != None ):
				isReseted = cfgNode[ 1 ]
			
			# ...
			if ( isReseted ):
				sequence.SetPivotOffset( MTUGetRotatePivotPosition( node ) )
			#sequence.SetPivotOffset( self.GetPivotOffset( node ) )
					
		cmds.currentTime( currentTime )
		
		# ...
		return sequenceInfo
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetPivotOffset( self, node ):
		offset = MTVector( 0, 0, 0 )
		
		if ( node != "Spine3" ):
			pivot  = MTUGetRotatePivotPosition( node )
			pos    = MTUGetPosition( node )			
			offset = ( pivot - pos )			

			"""
			parent = cmds.listRelatives( node, parent = True )
		
			if ( ( parent != None ) and ( len( parent ) > 0 ) ):
				offset += self.GetPivotOffset( parent [ 0 ] )
			"""
		
		return offset

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def	GetWorldPosition( self, node, frame ):
		myPos  = cmds.getAttr( node + ".translate", time = frame )[ 0 ]
		vPos   = MTVector( myPos[ 0 ], myPos[ 1 ], myPos[ 2 ] )
		
		if ( node != "Spine3" ):
			parent = cmds.listRelatives( node, parent = True )
		
			if ( ( parent != None ) and ( len( parent ) > 0 ) ):
				parentPos = self.GetWorldPosition( parent[ 0 ], frame )
				vPos      = vPos + parentPos			

		return vPos	
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetNodesWithTranslationKeys( self, nodes ):
		nodesWithKeys = [ ]
		
		if ( Config_UseOnlyNodesInList ):
			for node in Config_Nodes:
				# ... el nodo tiene que existir en la escena ...
				if ( cmds.objExists( node[ 0 ] ) ):
					nodesWithKeys.append( node[ 0 ] )
		else:
			for node in nodes:
				if ( cmds.attributeQuery( "translateX", node = node, exists = True ) == True ):
					has = ( cmds.keyframe( node + ".translateX", query = True, keyframeCount = True ) > 0 )
					has = has and ( cmds.keyframe( node + ".translateY", query = True, keyframeCount = True ) > 0 )
					has = has and ( cmds.keyframe( node + ".translateZ", query = True, keyframeCount = True ) > 0 )
			
					if ( has == True ):
						nodesWithKeys.append( node )
		
		return sorted( nodesWithKeys, key = unicode.lower )

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------		
	def ResetFrameMarkersUsed( self ):
		self.NumFrameMarkersUsed = 0

		# .. se hacen invisible los que hay creados ...
		for marker in self.FrameMarkers:
			cmds.hide( marker.GetGizmo() )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def ResetTranslationManipsUsed( self ):
		self.NumTranslationManipsUsed 	= 0
		
		# .. se hacen invisible los que hay creados ...
		for manip in self.TranslationManips:
			manip.DestroyTranslationScriptJobs()
			cmds.hide( manip.GetGizmo() )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetTranslationManip( self ):
		numManips = len( self.TranslationManips )		
		manip     = None
		
		self.NumTranslationManipsUsed += 1
		
		if ( self.NumTranslationManipsUsed >= numManips ):
			gizmo = cmds.polyCube( width = 2.5, height = 2.5, depth = 2.5 )[ 0 ]
			manip = Manip( gizmo )
			self.TranslationManips.append( manip )
		
			# ... scrip job para saber cuando se mueve ...
			manip.SetApp( self )
				
		else:
			manip = self.TranslationManips[ self.NumTranslationManipsUsed - 1 ]
			cmds.showHidden( manip.GetGizmo() )

		return manip
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def GetFrameMarker( self ):
		numMarkers = len( self.FrameMarkers )
		marker	   = None
		
		self.NumFrameMarkersUsed += 1
		
		if ( self.NumFrameMarkersUsed >= numMarkers ):
			gizmo  = cmds.polySphere( radius = 1.0 )[ 0 ]
			marker = FrameMarker( gizmo )
			self.FrameMarkers.append( marker )
		else:
			marker = self.FrameMarkers[ self.NumFrameMarkersUsed - 1 ]
			cmds.showHidden( marker.GetGizmo() )
			
		return marker
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def OnTranslationManipChange( self ):
		sequence 	 = next( ( seq for seq in self.SequenceInfo if seq.GetNode() == self.ActiveNode ), None )
		rebuildCurve = False
		
		# ... vemos que manipuladores estan seleccionados ...
		for node in self.SelectedNodes:
			selectManip = next( ( manip for manip in self.TranslationManips if manip.GetGizmo() == node ), None )

			if ( selectManip != None ):			
				# ... es un manipulador, se busca el frame al que pertenece ...
				frame = sequence.GetFrameWithTranslationManipGizmo( node )						
				
				if ( frame != None ):
					offset = MTUGetPosition( selectManip.GetGizmo() ) - selectManip.GetPosition()					
					frame.OnTranslationManipMove( offset )
					rebuildCurve = True
				
		# ...
		if ( rebuildCurve ):
			for i in range( self.StartFrame, self.EndFrame + 1 ):
				sequence.SetFramePosition( i - self.StartFrame, self.GetWorldPosition( sequence.GetNode(), i ) )
		
			self.CreateCurve()
	
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def OnSelectionChange( self ):
		self.SelectedNodes  = mel.eval( "ls -sl" )
		self.ActiveManip	= None

		# ... informacion del frame seleccionado ...		
		if ( ( self.SelectedNodes != None ) and ( len( self.SelectedNodes ) == 1 ) ):
			selectManip = None
			
			if ( self.TranslationManips != None ):
				selectManip = next( ( manip for manip in self.TranslationManips if manip.GetGizmo() == self.SelectedNodes[ 0 ] ), None )		
							
				if ( selectManip != None ):
					sequence  = next( ( seq for seq in self.SequenceInfo if seq.GetNode() == self.ActiveNode ), None )
					frameInfo = sequence.GetFrameInfo( selectManip.GetFrame() )
					self.ActiveManip =  selectManip
					
					cmds.checkBox( self.cXKey, edit = True, value = frameInfo.HasTranslationKeyAxis( 0 ) )
					cmds.checkBox( self.cYKey, edit = True, value = frameInfo.HasTranslationKeyAxis( 1 ) )
					cmds.checkBox( self.cZKey, edit = True, value = frameInfo.HasTranslationKeyAxis( 2 ) )
					cmds.text( self.txtSelectedFrame, edit = True, label = selectManip.GetFrame() + self.StartFrame )

			# ...
			self.EnableKeyInfo( ( selectManip != None ) )
		else:
			self.EnableKeyInfo( False )		
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def OnWindowClosed( self ):
		if ( len( self.TranslationManips ) > 0 ):
			for manip in self.TranslationManips:
				cmds.delete( manip.GetGizmo() )
				
			self.TranslationManips = [ ]
			
		# ...
		if ( len( self.FrameMarkers ) > 0 ):
			for mark in self.FrameMarkers:
				cmds.delete( mark.GetGizmo() )
				
			self.FrameMarkers = [ ]
			
		# ...
		if ( self.Curve != None ):
			cmds.delete( self.Curve )
			self.Curve = None
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------
	def ListNodesWithTranslationKeys( self ):
		cmds.textScrollList( self.listNodes, edit = True, removeAll = True )
		
		if ( self.NodesWithKeys != None ):
			cmds.textScrollList( self.listNodes, edit = True, append = self.NodesWithKeys )
			
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------			
	def OnListNodeSelected( self, *args ):
		self.SelectNode( cmds.textScrollList( self.listNodes, query = True, selectItem = True )[ 0 ] )

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------		
	def OnTextFrameInfoValueChange( self, *args ):
		self.StartFrame     = int( cmds.textField( self.txtStartFrame, query = True, text = True ) )
		self.EndFrame       = int( cmds.textField( self.txtEndFrame, query = True, text = True ) )
		self.EnableNodesList( False ) # si se cambia de frame hay que reanalizar la secuencia
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------		
	def OnAnalyze( self, *args ):
		self.AnalyzeSequence()
		self.EnableNodesList( True )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------		
	def OnKeyChange( self, *args ):
		checks  = [ cmds.checkBox( self.cXKey, query = True, value = True ), cmds.checkBox( self.cYKey, query = True, value = True ), cmds.checkBox( self.cZKey, query = True, value = True ) ]
		attribs = [ ".translateX", ".translateY", ".translateZ" ]
		
		# ... se quieren cambios? ...
		sequence  = next( ( seq for seq in self.SequenceInfo if seq.GetNode() == self.ActiveNode ), None )
		frameInfo = sequence.GetFrameInfo( self.ActiveManip.GetFrame() )
		
		# ...
		refreshCurve = False
		frame        = self.ActiveManip.GetFrame() + self.StartFrame
		
		for i in range( 0, 3 ):
			if ( checks[ i ] != frameInfo.HasTranslationKeyAxis( i ) ):
				if ( checks[ i ] ): # ... se crea la key ...
					cmds.setKeyframe( self.ActiveNode + attribs[ i ], insert = True, time = ( frame, frame ) )
					frameInfo.SetTranslationKey( i )
				else: # ... se borra la key ...
					#cmds.selectKey( self.ActiveNode + attribs[ i ], add = True, keyframe = True, time = ( frame, frame ) )
					cmds.cutKey( self.ActiveNode + attribs[ i ], time = ( frame, frame ), option = "keys" )
					frameInfo.RemoveTranslationKey( i )
					
				refreshCurve = True
				
		# ...
		if ( refreshCurve ):
			self.CreateCurve()

	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def OnRefreshCurve( self, *args ):
		if ( self.Curve != None ):
			self.CreateCurve()		
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def EnableKeyInfo( self, enable ):
		cmds.checkBox( self.cXKey, edit = True, enable = enable )
		cmds.checkBox( self.cYKey, edit = True, enable = enable )
		cmds.checkBox( self.cZKey, edit = True, enable = enable )
		
		if ( not enable ):
			cmds.text( self.txtSelectedFrame, edit = True, label = "None" )
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------	
	def EnableNodesList( self, enable ):	
		cmds.textScrollList( self.listNodes, edit = True, enable = enable )	
		
	#-------------------------------------------------------------
	#--
	#-------------------------------------------------------------			
	def BuildUI( self ):
		self.Window = cmds.window( title = self.WINDOW_NAME + " " + self.PLUGIN_VERSION, sizeable = True, resizeToFitChildren = True, widthHeight = ( self.WINDOW_WIDTH, self.WINDOW_HEIGHT ) )
		
		HalfWidth = ( self.WINDOW_WIDTH / 2 )

		# main column
		cmds.columnLayout()
		
		# ...
		cmds.frameLayout( label = "Sequence", collapsable = False, width = self.WINDOW_WIDTH )
		cmds.columnLayout()
		cmds.rowColumnLayout( numberOfColumns = 2, columnWidth = [ ( 1, 70 ), ( 2, self.WINDOW_WIDTH - 80 ) ] )
		cmds.text( label = "Start", align = "left" )
		self.txtStartFrame = cmds.textField( text = self.StartFrame, changeCommand = self.OnTextFrameInfoValueChange )
		cmds.text( label = "End", align = "left" )
		self.txtEndFrame = cmds.textField( text = self.EndFrame, changeCommand = self.OnTextFrameInfoValueChange )
		cmds.setParent( ".." ) #rowColumnLayout
		
		cmds.rowColumnLayout( numberOfColumns = 2, columnWidth = [ ( 1, HalfWidth - 4 ), ( 2, HalfWidth - 4 ) ] )
		self.bAnalyze = cmds.button( label = "Analyze", command = self.OnAnalyze )
		self.bRefreshCurve = cmds.button( label = "Refresh Curve", command = self.OnRefreshCurve, enable = False )
		cmds.setParent( ".." ) #rowColumnLayout
		
		cmds.setParent( ".." ) # columnLayout
		cmds.setParent( ".." ) # frameLayout		
			
		# 
		cmds.frameLayout( label = "Frame Selected Info", collapsable = False, width = self.WINDOW_WIDTH )
		cmds.columnLayout()
		self.txtSelectedFrame = cmds.text( label = "None", align = "left" )
		cmds.rowColumnLayout( numberOfColumns = 3, columnWidth = [ ( 1, self.WINDOW_WIDTH / 3 ), ( 2, self.WINDOW_WIDTH / 3 ), ( 3, self.WINDOW_WIDTH / 3 ) ] )
		self.cXKey = cmds.checkBox( label = "X Key", value = False, changeCommand = self.OnKeyChange )
		self.cYKey = cmds.checkBox( label = "Y Key", value = False, changeCommand = self.OnKeyChange )
		self.cZKey = cmds.checkBox( label = "Z Key", value = False, changeCommand = self.OnKeyChange )		
		cmds.setParent( ".." ) #rowColumnLayout
		cmds.setParent( ".." ) #columnLayout		
		cmds.setParent( ".." ) # frameLayout		
		
		# ...
		cmds.frameLayout( label = "Nodes", collapsable = False, width = self.WINDOW_WIDTH )
		cmds.columnLayout()
		self.listNodes = cmds.textScrollList( numberOfRows = 1, allowMultiSelection = False, height = 200, selectCommand = self.OnListNodeSelected )
		cmds.setParent( ".." ) #columnLayout		
		cmds.setParent( ".." ) # frameLayout		

		# ...
		cmds.showWindow( self.Window ) # main column