#    (C) Roan LaPlante 2013 rlaplant@nmr.mgh.harvard.edu
#
#	 This file is part of cvu, the Connectome Visualization Utility.
#
#    cvu is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


from traits.api import (HasTraits,Bool,Event,File,Int,Str,Directory,Function,
	Enum,List,Button,Range,Instance,Float,Trait,CFloat)
from traitsui.api import (Handler,View,Item,OKCancelButtons,OKButton,Spring,
	Group,ListStrEditor,CheckListEditor,HSplit,FileEditor,VSplit,Action,HGroup,
	TextEditor,ImageEnumEditor,UIInfo,Label,VGroup,ListEditor)
from traitsui.file_dialog import open_file
import os; import cvu_utils as util;
from color_map import CustomColormap
from custom_file_editor import CustomFileEditor, CustomDirectoryEditor

from traits.api import on_trait_change

class InteractiveSubwindow(Handler):
	finished=Bool(False)
	notify=Event

	info=Instance(UIInfo)

	def init_info(self,info):
		self.info=info
	def closed(self,info,is_ok):
		info.object.finished=is_ok
		info.object.notify=True
	def reconstruct(self,info=None):
		if info is None:
			info=self.info
		info.ui.dispose()
		info.object.edit_traits()

def append_proper_buttons(buttonlist):
	#get around list mutability
	buttonlist.extend(OKCancelButtons)
	return buttonlist

class OptionsWindow(InteractiveSubwindow):
	surface_visibility = Range(0.0,1.0,.15)
	circ_size = Range(7,20,10,mode='spinner')
	conns_colorbar=Bool(False)
	scalar_colorbar=Bool(False)
	pthresh = Range(0.0,1.0,.95)
	nthresh = Float
	thresh_type = Enum('prop','num')
	prune_modules = Bool(True)
	show_floating_text = Bool(True)
	module_view_style = Enum('intramodular','intermodular','both')
	render_style=Enum('glass','cracked_glass','contours','wireframe','speckled')
	conns_disclaimer=Str
	interhemi_conns_on = Bool(True)
	lh_conns_on = Bool(True)
	rh_conns_on = Bool(True)
	lh_nodes_on = Bool(True)
	rh_nodes_on = Bool(True)
	lh_surfs_on = Bool(True)
	rh_surfs_on = Bool(True)
	conns_width = Float(2.)
	conns_colors_on = Bool(True)

	intermediate_graphopts_list=List(Str)
	initial_graphopts_list=List(Str)
	modules_list=List(Str)
	traits_view=View(
		VGroup(
			HSplit(
				Item(name='circ_size'),
				Item(name='conns_width',label='conn linewidth'),
				Item(name='show_floating_text',label='floating 3D text on'),
			),
			HSplit(
				Item(name='pthresh'),
				Item(name='nthresh'),
				Item(name='thresh_type'),
			),
			HSplit(
				Item(name='render_style',label='surface style'),
				Item(name='surface_visibility',label='surface opacity'),
			),
			HSplit(
				Item(name='module_view_style',label='module connection style'),
				#Item(name='prune_modules',label='prune singleton modules'),
			),
			HSplit(
				Item(name='interhemi_conns_on',
					label='interhemispheric conns on'),
				Item(name='lh_conns_on',label='LH conns on'),
				Item(name='rh_conns_on',label='RH conns on'),
			),
			HSplit(
				Item(name='lh_nodes_on',label='LH nodes on'),
				Item(name='rh_nodes_on',label='RH nodes on'),
			),
			HSplit(
				Item(name='lh_surfs_on',label='LH surfaces on'),
				Item(name='rh_surfs_on',label='RH surfaces on'),
			),
			HSplit(
				Item(name='conns_colorbar',label='show conns colorbar'),
				Item(name='scalar_colorbar',label='show scalar colorbar'),
				Item(name='conns_colors_on'),
			),
			HSplit(
				Item(name='conns_disclaimer',style='readonly',height=10,
					width=550,show_label=False)
			),
			label='Display options',show_labels=False
		),
		VGroup(
			Item(name='intermediate_graphopts_list',editor=CheckListEditor(
				name='initial_graphopts_list'),show_label=False,
				style='custom'),
			label='Graph statistics',show_labels=False
		),
		kind='live',buttons=OKCancelButtons,
		title='Select your desired destiny',
	)

	def _initial_graphopts_list_default(self):
		return ['global efficiency', 'local efficiency', 'average strength',
			'clustering coefficient', 'eigenvector centrality', 'modularity', 
			'participation coefficient', 'within-module degree']
	def _intermediate_graphopts_list_default(self):
		return ['global efficiency', 'clustering coefficient']
	def _conns_disclaimer_default(self):
		return ("Note changing conn visibility is not applied immediately as "
			"it can be costly. To force application, click 'Reset Display'")

class GraphTheoryWindow(InteractiveSubwindow):
	from graph import StatisticsDisplay

	graph_stats=List(StatisticsDisplay)
	current_stat=Instance(StatisticsDisplay)
	scalar_savename=Str

	RecalculateButton=Action(name='Recalculate',action='do_recalculate')
	RecalculateEvent=Event

	SaveToScalarButton=Action(name='Save to scalar',action='do_sv_scalar')
	SaveToScalarEvent=Event
	
	traits_view=View(
		VGroup(
			HGroup(
			Item('graph_stats',style='custom',show_label=False,
				editor=ListEditor(use_notebook=True,page_name='.name',
				selected='current_stat')),
			),HGroup(
			Item('scalar_savename',label='Scalar name',
				height=25,width=180),
			),
		),
		height=400,width=350,
		title='Mid or feed',kind='live',
		buttons=[RecalculateButton,SaveToScalarButton,OKButton,])

	def _current_stat_changed(self):
		self.scalar_savename=self.current_stat.name

	#handler methods
	def do_sv_scalar(self,info):
		self.SaveToScalarEvent=True

	def do_recalculate(self,info):
		self.RecalculateEvent=True

class CustomColormapWindow(InteractiveSubwindow):
	#first argument is class, second is default value.
	default_map=Instance(CustomColormap,CustomColormap('default'))
	scalar_map=Instance(CustomColormap,CustomColormap('scalar'))
	activation_map=Instance(CustomColormap,CustomColormap('activation'))
	connmat_map=Instance(CustomColormap,CustomColormap('connmat'))

	EditCmapButton = Action(name='Colormap customizer',action='do_edit_cmap')
	ResetDefaultsButton = Action(name='Reset defaults',action='do_defaults')

	def cmap_group_view(m):
		return Group(Item(name='label',style='readonly',object=m),
					Item(name='cmap',object=m,
						editor=ImageEnumEditor(path=CustomColormap.imgs_path,
							values=CustomColormap.lut_list,cols=7)),
					Item(name='fname',editor=CustomFileEditor(),object=m,
						enabled_when='%s.cmap==\'file\''%m),
					HGroup(
						Item(name='reverse',object=m)
					),
					Item(name='threshold',object=m,
						enabled_when='%s.cmap==\'custom_heat\''%m),
					show_labels=False)

	traits_view=View(
		HGroup(
			cmap_group_view('default_map'),
			cmap_group_view('scalar_map'),
			cmap_group_view('activation_map'),
			cmap_group_view('connmat_map')
		),
		kind='live',
		buttons=append_proper_buttons([EditCmapButton,ResetDefaultsButton]),
		title='If it were up to me it would all be monochrome',
	)

	#handler methods
	def do_edit_cmap(self,info):
		from tvtk import util as tvtk_util; import sys,subprocess
		script=os.path.join(os.path.dirname(tvtk_util.__file__),
			'wx_gradient_editor.py')
		subprocess.Popen([sys.executable, script])

	def do_defaults(self,info):
		for map in [self.default_map,self.scalar_map,self.activation_map,
				self.connmat_map]:
			map.reset_traits(['cmap','fname','reverse','threshold'])

	def edit_traits(self):
		super(CustomColormapWindow,self).edit_traits(context=
			{'default_map':self.default_map,
			 'scalar_map':self.scalar_map,
			 'activation_map':self.activation_map,
			 'connmat_map':self.connmat_map,
			 'object':self})

class RequireWindow(InteractiveSubwindow):
	require_ls=List(Str)
	please_note=Str('Enter the ROIs you would like to force to display on the '
		'circle plot.  You must spell them precisely, e.g. "lh_frontalpole"')
	traits_view=View(
		Item(name='please_note',style='readonly',height=35,width=250),
		Item(name='require_ls',editor=ListStrEditor(auto_add=True,
			editable=True),label='List ROIs here'),
		buttons=OKCancelButtons,title='Mango curry')

class AdjmatChooserWindow(InteractiveSubwindow):
	Please_note=Str("All but first field are optional.  Specify adjmat order "
		"if the desired display order differs from the existing matrix order."
		"  Specify unwanted channels as 'delete' in the label order.  Data "
		"field name applies to the data field for .mat matrices only.")
	adjmat=File
	open_adjmat=Button('Browse')
	open_adjmat_order=Button('Browse')
	#adjmat_order=Trait(None,None,File)
	adjmat_order=File
	max_edges=Int
	field_name=Str('adj_matrices')
	ignore_deletes=Bool
	require_window=Instance(InteractiveSubwindow,())
	RequireButton=Action(name='force display of ROIs',action='do_rw_show')
	traits_view=View(
		Item(name='Please_note',style='readonly',height=140,width=250),
		#HSplit(
		#	Item(name='adjmat',style='text'),
		#	Item(name='open_adjmat',show_label=False),
		#),
		Item(name='adjmat',
			editor=CustomFileEditor()),
		Item(name='adjmat_order',label='Label Order',
			editor=CustomFileEditor()),
		#HSplit(
		#	Item(name='adjmat_order',style='text'),
		#	Item(name='open_adjmat_order',show_label=False),
		#),
		Item(name='max_edges',label='Max Edges'),
		Item(name='field_name',label='Data Field Name'),
		Item(name='ignore_deletes',label='Ignore deletes'),
		kind='live',buttons=append_proper_buttons([RequireButton]),
		title='Report all man-eating vultures to security',)

	#private methods
	def _open_adjmat_fired(self):
		self.adjmat=open_file()
		self.edit_traits()
	def _open_adjmat_order_fired(self):
		self.adjmat_order=open_file()
		self.edit_traits()
	def _require_window_default(self):
		return RequireWindow()

	#handler methods
	def do_rw_show(self,info):
		info.object.require_window.edit_traits()

class ParcellationChooserWindow(InteractiveSubwindow):
	Please_note=Str('fsaverage5 is fine unless individual morphology '
		'is of interest.  Visualizing tractography requires individual '
		'morphology.')
	SUBJECTS_DIR=Directory('./')
	SUBJECT=Str('fsavg5')
	labelnames_f=File
	open_labelnames_f=Button('Browse')
	parcellation_name=Str
	DisposeEvent=Action(action='do_dispose')
	traits_view=View(
		Group(
			Item(name='Please_note',style='readonly',height=85,width=250),
			Item(name='SUBJECT'),
			Item(name='SUBJECTS_DIR',editor=CustomDirectoryEditor()),
			Item(name='parcellation_name',label='Parcellation'),
			Item(name='labelnames_f',label='Label Display Order',
				editor=CustomFileEditor()),
			#HSplit(
			#	Item(name='labelnames_f',label='Label Display Order',
			#		style='text',springy=True),
			#	Item(name='open_labelnames_f',show_label=False)
			#),
		), kind='live',buttons=OKCancelButtons,
			title="This should not be particularly convenient",)

	def _open_labelnames_f_fired(self):
		self.labelnames_f=open_file()
		self.do_dispose(self.info)
		self.edit_traits()

	def _reconstruct(self):
		self.do_dispose(self.info)
		self.edit_traits()

class TractographyChooserWindow(InteractiveSubwindow):
	Please_note=Str('Tractography will be misaligned with the surface unless '
		'the surface corresponds to the subject\'s individual morphology.\n'
		'cvu will source the freesurfer setup script.  You can omit this if '
		'the environment has already been set prior to running cvu.  All four '
		'of the other fields are required.')
	track_file=File
	b0_volume=File
	SUBJECTS_DIR=Directory
	SUBJECT=Str
	fs_setup=File('/usr/local/freesurfer/nmr-stable53-env')
	traits_view=View(
		Group(
			Item(name='Please_note',style='readonly',height=125,width=325),
			Item(name='track_file',editor=CustomFileEditor()),
			Item(name='b0_volume',editor=CustomFileEditor()),
			Item(name='SUBJECTS_DIR',editor=CustomDirectoryEditor()),
			Item(name='SUBJECT'),
			Item(name='fs_setup',editor=CustomFileEditor()),
		), kind='live',buttons=OKCancelButtons,
			title='Just FYI subject 39108 has an abnormal HRF')

class LoadGeneralMatrixWindow(InteractiveSubwindow):
	Please_note=Str('Same rules for adjmat ordering files apply')
	mat=File
	open_mat=Button('Browse')
	mat_order=File
	field_name=Str
	ignore_deletes=Bool
	whichkind=Enum('modules','scalars')
	dataset_nr=Int(1)
	dataset_name=Str('dataset1')
	traits_view=View(
		Item(name='Please_note',style='readonly',height=50,width=250),
		Item(name='mat',label='Filename',editor=CustomFileEditor()),
		#HSplit(
		#	Item(name='mat',label='Filename',style='text',springy=True),
		#	Item(name='open_mat',show_label=False),
		#),
		#Item(name='mat',label='Filename',editor=FileEditor(entries=10),style='simple'),
		Item(name='mat_order',label='Ordering file',editor=CustomFileEditor()),
		Item(name='field_name',label='Field (.mat files only)'),
		Item(name='ignore_deletes',label='Ignore deletes'),
		Item(name='dataset_name',label='Name this dataset'),
		kind='live',buttons=OKCancelButtons,
		title='Behold the awesome power of zombies')

	def _open_mat_fired(self):
		#self.mat=open_file()
		res=util.file_chooser(initialdir=os.path.dirname(self.mat),
			title='Roentgenium is very useful')
		if len(res)>0:
			self.mat=res

	def dataset_plusplus(self):
		self.dataset_nr+=1
		self.dataset_name='dataset%i' % self.dataset_nr

class ConfigureScalarsWindow(InteractiveSubwindow):
	#idea:
	#node_scalars needs to be DICTIONARY.
	#add field to dictionary upon load scalars.  can replace.
	#three ListStr editors, one for each display method, across the field names
	#the selections can be the same for multiple scalars
	scalar_sets=List(Str)
	nod_col=Str
	nc_str=Str('Node color')
	srf_col=Str
	sc_str=Str('Surface color')
	nod_siz=Str
	ns_str=Str('Node size')
	circle=Str
	circ_str=Str('Circle plot')
	conmat=Str
	cmat_str=Str('Connection Matrix')
	traits_view=View(
		HGroup(
			Group(
				Item('nc_str',style='readonly'),
				Item('scalar_sets',editor=ListStrEditor(selected='nod_col')),
				show_labels=False
			),
			Group(
				Item('sc_str',style='readonly'),
				Item('scalar_sets',editor=ListStrEditor(selected='srf_col')),
				show_labels=False
			),
			Group(
				Item('ns_str',style='readonly'),
				Item('scalar_sets',editor=ListStrEditor(selected='nod_siz')),
				show_labels=False
			),
			Group(
				Item('circ_str',style='readonly'),
				Item('scalar_sets',editor=ListStrEditor(selected='circle')),
				show_labels=False
			),
			Group(
				Item('cmat_str',style='readonly'),
				Item('scalar_sets',editor=ListStrEditor(selected='conmat')),
				show_labels=False
			),
		),
		height=200,width=800,buttons=OKCancelButtons,
		title='Your data is probably just spurious artifacts anyway',
	)
	
class NodeChooserWindow(InteractiveSubwindow):
	node_list=List(Str)
	cur_node=Int(-1)
	traits_view=View(
		Item(name='node_list',editor=
			ListStrEditor(selected_index='cur_node'),show_label=False),
		kind='live',height=350,width=350,buttons=OKCancelButtons,
		resizable=True,title='Do you know the muffin man?')

class ModuleChooserWindow(InteractiveSubwindow):
	module_list=List(Str)
	cur_mod=Int(-1)
	traits_view=View(
		Item(name='module_list',
			editor=ListStrEditor(editable=True,selected_index='cur_mod'),
			show_label=False),
		kind='live',height=350,width=350,buttons=OKCancelButtons,
		resizable=True,title='Roll d12 for dexterity check')

class ModuleCustomizerWindow(InteractiveSubwindow):
	initial_node_list=List(Str)
	intermediate_node_list=List(Str)
	return_module=List(Int)
	ClearButton=Action(name='Clear Selections',action='do_clear')
	traits_view=View(
		Item(name='intermediate_node_list',editor=CheckListEditor(
			name='initial_node_list',cols=2),show_label=False,style='custom'),
		kind='live',height=400,width=500,
		buttons=append_proper_buttons([ClearButton]),
		resizable=True,scrollable=True,title='Mustard/Revolver/Conservatory')

	#index_convert may return a ValueError, it should be
	#contained in try/except from higher up.
	def index_convert(self):
		self.return_module=[self.initial_node_list.index(i)
			for i in self.intermediate_node_list]

	#handler methods
	def do_clear(self,info):
		info.object.intermediate_node_list=[]

class SaveSnapshotWindow(InteractiveSubwindow):
	savefile=Str(os.environ['HOME']+'/')
	dpi=Int(300)
	whichplot=Enum('3D brain','connection matrix','circle plot')
	traits_view=View(Group(
		Item(name='savefile'),
		Item(name='whichplot',label='view'),
		Item(name='dpi',label='dots per inch'),
	), kind='live',buttons=OKCancelButtons,
		title="Help I'm a bug",height=250,width=250)

class MakeMovieWindow(InteractiveSubwindow):
	savefile=Str(os.environ['HOME']+'/')
	framerate=Int(20)
	bitrate=Int(4000) 
	samplerate=Int(8)
	#use x11grab exclusively.  remove snapshots altogether eventually
	type=Enum('x11grab','snapshots')
	anim_style=Bool(True)
	animrate=Int(8)
	traits_view=View(Group(
		Item(name='savefile'),
		Item(name='framerate',label='framerate'),
		Item(name='bitrate',label='bitrate (kb/s)'),
		Item(name='anim_style',label='automatically rotate'),
		Item(name='samplerate',label='animation speed'),
	), kind='live',buttons=OKCancelButtons,
		title="Make me a sandwich",height=250,width=450)

class ReallyOverwriteFileWindow(InteractiveSubwindow):
	Please_note=Str('That file exists.  Really overwrite?')
	save_continuation=Function # Continuation passing style
	traits_view=View(Spring(),
		Item(name='Please_note',style='readonly',height=25,width=250,
			show_label=False),
		Spring(),
		kind='live',buttons=OKCancelButtons,
		title='Your doom awaits you')

class ErrorDialogWindow(HasTraits):
	error=Str
	traits_view=View(Item(name='error',style='readonly',height=75,width=300),
		buttons=[OKButton],kind='nonmodal',
		title='Evil mutant zebras did this',)

class WarningDialogWindow(HasTraits):
	warning=Str
	traits_view=View(Item(name='warning',style='readonly',height=75,width=300),
		buttons=[OKButton],kind='nonmodal',
		title='Evil mutant zebras did this',)

class AboutWindow(HasTraits):
	message=Str('cvu version 0.2\n'
		'cvu is copyright (C) Roan LaPlante 2013\n\n'
		'cvu strictly observes the tenets of fundamentalist Theravada Mahasi\n'
		'style Buddhism.  Any use of cvu in violation of the tenets of\n'
		'fundamentalist Theravada Mahasi style Buddhism or in violation of\n'
		'the theosophical or teleological principles as described\n'
		'in the Vishuddhimagga Sutta is strictly prohibited and punishable by\n'
		'extensive Mahayana style practice.  By being or not being mindful of\n'
		'the immediate present moment sensations involved in the use of cvu,\n'
		'you confer your acceptance of these terms and conditions.\n\n'

		'cvu is distributed without warranty unless otherwise prohibited by\n'
		'law.  cvu is licensed under the GNU GPL v3.  a license is contained\n'
		'with the distribution of this program.  you may modify and convey\n'
		'this program to others in accordance with the terms of the GNU GPLv3\n'		'or optionally any subsequent version of the GNU GPL.'
	)
	traits_view=View(Item(name='message',style='readonly',show_label=False),
		buttons=[OKButton],kind='nonmodal',height=300,width=300,
		title='Greetings, corporeal being',)
