# Licensed under a 3-clause BSD style license - see LICENSE.rst
# This is the new WFIRST Jupyter Notebook GUI - it should replace the previous notebook utils, which
# were written for a much older version of iPyWidgets.

from __future__ import division, absolute_import

import os
import json

import matplotlib
from matplotlib import style
style.use('ggplot')
matplotlib.use('nbagg')
import matplotlib.pyplot as plt

from pandeia.engine.perform_calculation import perform_calculation
from pandeia.engine.io_utils import read_json, write_json
from pandeia.engine.calc_utils import build_default_calc, build_default_source

from ipywidgets import widgets
from IPython.display import display, clear_output
import traitlets

refdata = os.environ['pandeia_refdata']

dummy = None
geom_mapping = {'Point Source': 'point', 'Flat':'flat', 'Power Law': 'power', '2D Gaussian': 'gaussian2d',
                'Sersic (Effective Radius)': 'sersic', 'Sersic (Scale Radius)': 'sersic_scale'}
norm_mapping = {'infinity': 'integ_infinity', 'scale radius': 'surf_scale', 'center': 'surf_center'}

"""
Functions to aid in creating valid tests and identifying valid instrument configurations.
"""


class Instrument():
    """
    Class for parsing valid instrument configurations from config.json files.
    This is primarily in aid of generating tests, but can be used for anything
    that needs to find valid instrument configurations.

    Given a telescope and instrument, class objects will expose the available
     modes.
    If a mode is set, the class object will expose available apertures and
     strategies for that mode.
    If an aperture is set as well, the class object will expose the valid
     filters, dispersers, readmodes, and subarrays,

    The remainder of the instrument configuration is available as self.config

    Parameters
    ----------
    instrument; string
        One of the instruments defined in pandeia_refdata.
    telescope: string
        Telescope defined in pandeia_refdata. Currently 'jwst', 'wfirst',
        or 'hst'
    webapp: bool
        Change this attribute to True to enable stricter filter lists
    """

    def __init__(self,instrument, telescope):
        self.instrument = instrument
        self.telescope = telescope
        self.data_dir = os.environ['pandeia_refdata']
        config_file = open('{0:}/{1:}/{2:}/config.json'.format(self.data_dir,self.telescope,self.instrument))
        self.config = json.load(config_file)
        self.webapp = False
        self.get_modes()

    def get_modes(self):
        self.modes = self.config['modes']

    def set_mode(self, mode):
        self.mode = mode
        self.get_apertures()
        self.get_strategies()

    def set_element(self, element, value):
        setattr(self,element,value)

    def get_apertures(self):
        self.apertures_all = self.config['apertures']

        if 'apertures' in self.config['mode_config'][self.mode]:
            self.apertures = self.config['mode_config'][self.mode]['apertures']
        else:
            self.apertures = self.apertures_all

    def set_aperture(self,aperture):
        self.aperture = aperture
        self._lookup('dispersers')
        self._lookup('filters')
        self._lookup('subarrays')
        self._lookup('readmodes')

    def _lookup(self,element):
        setattr(self,'{0:}_all'.format(element),self.config[element])

        if element in self.config['mode_config'][self.mode]:
            setattr(self, element, self.config['mode_config'][self.mode][element])
        else:
            # if it's not found in mode_config, use the base list
            setattr(self, element, getattr(self,'{0:}_all'.format(element)))

        # Web constraints will remove some more items
        if self.webapp:
            self.constrain(element=element)

        if getattr(self,element) == []:
            setattr(self, element, [None])

    def get_strategies(self):
        self.strategies = self.config['strategy_config'][self.mode]['permitted_methods']

    def constrain(self, element=None, constrain_on='aperture'):
        # Config Constraints lists dispersers in one of four ways:
        # Under apertures/dispersers/<mode>
        # Under apertures/dispersers/default if it applies to all modes but a particular one
        # Under apertures/dispersers if it applies to ALL modes
        # If unlisted, use the mode or global values.

        # NIRSpec also constrains by disperser.

        survivors = None
        constraint = '{0:}s'.format(constrain_on)
        # Three things required to do this:
        # 1. The configuration dictionary must have a config_constraints section
        # 2. The element to constrain on must be defined (for example, aperture)
        # 3. The element to constrain on must be in the config_constraints section (as, example, apertures)
        if 'config_constraints' in self.config:
            if hasattr(self,constrain_on):
                const = getattr(self,constrain_on)
                if constraint in self.config['config_constraints']:
                    if const in self.config['config_constraints'][constraint]:
                        if element in self.config['config_constraints'][constraint][const]:
                            if self.mode in self.config['config_constraints'][constraint][const][element]:
                                survivors = self.config['config_constraints'][constraint][const][element][self.mode]
                            elif "default" in self.config['config_constraints'][constraint][const][element]:
                                survivors = self.config['config_constraints'][constraint][const][element]['default']
                            else:
                                survivors = self.config['config_constraints'][constraint][const][element]

        # only actually set a new list if there's something worth setting.
        if survivors is not None:
            setattr(self,element,survivors)


def get_config(filename):
    """
    read configuration data from a JSON file and create a dict using display_strings as the keys.
    these dicts will be used to populate pull-downs with descriptive names, but provide lookup to
    the values that need to be passed back to the engine.

    Parameters
    ----------
    filename: string
        filename of JSON config file to Load

    Returns
    -------
    conf: dict
        JSON configuration data with keys swapped out for display_strings where available.
    """
    conf_data = read_json(filename)
    conf = {}
    for k in conf_data:
        if "display_string" in conf_data[k]:
            conf[conf_data[k]["display_string"]] = k
        else:
            conf[k] = k
    return conf


class SourceObj(object):
    """
    A source definition block. It's comprised of three main blocks:
    Flux
    SED
    Advanced

    The Advanced block has three sub-blocks:
    Geometry
    Position
    Redshift and Extinction
    """
    def __init__(self):
        self.container = widgets.VBox(width="100%", background_color="#EEEEEE")

        # Flux
        self.flux_box = widgets.HBox(padding='10px', width="100%")
        self.flux = widgets.BoundedFloatText(description="Source flux: ", min=0.0, max=1.0e30, value=23.0)
        self.funits = widgets.Dropdown(value='abmag', options=['abmag', 'njy', 'ujy', 'mjy', 'jy'])
        atwave = widgets.HTML(value=" at ", margin='5px')
        self.wave = widgets.BoundedFloatText(min=0.1, max=99999.0, value=1.5)
        waveunits = widgets.HTML(value="microns", margin='5px')
        self.flux_box.children = [self.flux, self.funits, atwave, self.wave, waveunits]

        # SED
        self.sed_box = widgets.HBox(padding='10px', width="100%")
        self.sed_select = widgets.Dropdown(
            description="SED type: ",
            options=['flat', 'phoenix', 'blackbody', 'extragalactic', 'star', 'power-law'],
            value='flat'
        )
        self.bb_temp = widgets.BoundedFloatText(description="Temp (K): ", min=0.0, max=99999.0, value=6500.0, width=75)
        phoenix_config_file = os.path.join(refdata, 'sed', 'phoenix', 'spectra.json')
        self.phoenix_config = get_config(phoenix_config_file)
        self.phoenix = widgets.Dropdown(options=sorted(self.phoenix_config))
        gal_config_file = os.path.join(refdata, 'sed', 'brown', 'spectra.json')
        self.gal_config = get_config(gal_config_file)
        self.galaxies = widgets.Dropdown(options=sorted(self.gal_config))
        star_config_file = os.path.join(refdata, 'sed', 'hst_calspec', 'spectra.json')
        self.star_config = get_config(star_config_file)
        self.star = widgets.Dropdown(options=sorted(self.star_config))
        self.pl_index = widgets.FloatText(description="Index: ", value=1.0, width=50)

        # We have to define anything we're going to use from the beginning, so we do that, and then
        # run the helper function that displays the selected (default) item and hides the rest.
        self.on_sed_change(dummy)
        self.sed_box.children = [self.sed_select, self.phoenix, self.pl_index, self.bb_temp, self.star, self.galaxies]
        self.sed_select.observe(self.on_sed_change)

        # Advanced
        # Geometry
        # The selector goes in one box, and all the geometry selections goes in another so that items can be activated/
        # deactivated as needed.
        self.geom_box = widgets.VBox(width="100%")
        self.source_box = widgets.HBox(width="100%")
        #profile_config_file = os.path.join(refdata, 'source', 'config.json')
        #self.profile_config = get_config(profile_config_file)
        self.src_select = widgets.Dropdown(description="Profile: ", options=['Point Source', 'Flat', '2D Gaussian',
                                                                             'Sersic (Effective Radius)', 'Sersic (Scale Radius)',
                                                                             'Power Law'],
                                             value='Point Source')
        self.source_box.children = [self.src_select]
        self.prof_box = widgets.VBox(width="100%")

        style = {'description_width': 'initial'}

        # We have to define anything we're going to use from the beginning, so we do that, and then
        # run the helper function that displays the selected (default) item and its attendant pieces, and hides the rest.
        self.major = widgets.FloatText(description="Semimajor (arcsec): ", value=0.5, style=style)
        self.minor = widgets.FloatText(description="Semiminor (arcsec): ", value=0.25, style=style)
        self.r_core = widgets.FloatText(description="Core Radius (arcsec): ", value=0.005, style=style)
        self.pos_a = widgets.BoundedFloatText(description="Orientation (deg): ", value=0, min=0, max=359.9, style=style)
        self.sersic = widgets.FloatSlider(description="Sersic Index: ", value=0.5, min=0.3, max=4, readout_format='.1f', style=style)
        self.power = widgets.FloatSlider(description="Power Index: ", value=1, min=0.1, max=10, style=style)
        self.norm = widgets.Dropdown(description="Normalize at: ", options=['infinity', 'scale radius', 'center'], style=style)
        self.norm_flat = widgets.Dropdown(description="Normalize at: ", options=['infinity', 'center'], style=style)
        self.prof_box.children = [self.major, self.minor, self.r_core, self.pos_a, self.norm, self.sersic, self.power]
        self.prof_box.children = [self.major, self.minor, self.pos_a, self.norm, self.sersic]
        self.geom_box.children = [self.source_box, self.prof_box]

        # Position
        self.pos_box = widgets.HBox(padding='10px', width="100%")
        self.pos_x = widgets.BoundedFloatText(description="X Position: ", min=-37.5, max=37.5)
        self.pos_y = widgets.BoundedFloatText(description="Y Position: ", min=-37.5, max=37.5)
        self.pos_box.children = [self.pos_x, self.pos_y]

        # Redshift and Extinction
        self.red_box = widgets.HBox(padding='10px', width="100%")
        self.redshift = widgets.BoundedFloatText(description="Redshift:", min=0.0, max=99999.0, value=0.0, width=70)
        self.red_box.children = [self.redshift]

        self.advanced_options = widgets.Accordion(children=[self.pos_box, self.geom_box, self.red_box])
        self.advanced_options.set_title(0,"Position")
        self.advanced_options.set_title(1,"Geometry")
        self.advanced_options.set_title(2,"Redshift")
        self.advanced_options.selected_index = None

        self.advanced_drop = widgets.Accordion(children=[self.advanced_options])
        self.advanced_drop.set_title(0, "ADVANCED")
        self.advanced_drop.selected_index = None
        self.container.children = [self.flux_box, self.sed_box, self.advanced_drop]

        self.on_prof_change(dummy)
        self.src_select.observe(self.on_prof_change)

    def on_sed_change(self, change):
        # For each possible setting of sed, flip the individual dropdown box sets on and off accordingly.
        if self.sed_select.value == "flat":
            self.bb_temp.layout.display = 'none'
            self.phoenix.layout.display = 'none'
            self.galaxies.layout.display = 'none'
            self.star.layout.display = 'none'
            self.pl_index.layout.display = 'none'
        elif self.sed_select.value == "phoenix":
            self.bb_temp.layout.display = 'none'
            self.phoenix.layout.display = "inline"
            self.galaxies.layout.display = 'none'
            self.star.layout.display = 'none'
            self.pl_index.layout.display = 'none'
        elif self.sed_select.value == "blackbody":
            self.bb_temp.layout.display = "inline"
            self.phoenix.layout.display = 'none'
            self.galaxies.layout.display = 'none'
            self.star.layout.display = 'none'
            self.pl_index.layout.display = 'none'
        elif self.sed_select.value == "extragalactic":
            self.bb_temp.layout.display = 'none'
            self.phoenix.layout.display = 'none'
            self.galaxies.layout.display = "inline"
            self.star.layout.display = 'none'
            self.pl_index.layout.display = 'none'
        elif self.sed_select.value == "star":
            self.bb_temp.layout.display = 'none'
            self.phoenix.layout.display = 'none'
            self.galaxies.layout.display = 'none'
            self.star.layout.display = "inline"
            self.pl_index.layout.display = 'none'
        elif self.sed_select.value == "power-law":
            self.bb_temp.layout.display = 'none'
            self.phoenix.layout.display = 'none'
            self.galaxies.layout.display = 'none'
            self.star.layout.display = 'none'
            self.pl_index.layout.display = 'inline'

    def on_prof_change(self,change):
        # For each possible setting of source, flip the properties boxes on and off accordingly.
        if self.src_select.value == "Point Source":
            self.major.layout.display = 'none'
            self.minor.layout.display = 'none'
            self.pos_a.layout.display = 'none'
            self.sersic.layout.display = 'none'
            self.power.layout.display = 'none'
            self.r_core.layout.display = 'none'
            self.norm.layout.display = 'none'
            self.norm_flat.layout.display = 'none'
        elif self.src_select.value == "2D Gaussian":
            self.major.layout.display = 'inline'
            self.minor.layout.display = 'inline'
            self.pos_a.layout.display = 'inline'
            self.sersic.layout.display = 'none'
            self.power.layout.display = 'none'
            self.r_core.layout.display = 'none'
            self.norm.layout.display = 'inline'
            self.norm_flat.layout.display = 'none'
        elif self.src_select.value == "Flat":
            self.major.layout.display = 'inline'
            self.minor.layout.display = 'inline'
            self.pos_a.layout.display = 'inline'
            self.sersic.layout.display = 'none'
            self.power.layout.display = 'none'
            self.r_core.layout.display = 'none'
            self.norm.layout.display = 'none'
            self.norm_flat.layout.display = 'inline'
        elif self.src_select.value == "Sersic (Scale Radius)":
            self.major.layout.display = 'inline'
            self.minor.layout.display = 'inline'
            self.pos_a.layout.display = 'inline'
            self.sersic.layout.display = 'inline'
            self.power.layout.display = 'none'
            self.r_core.layout.display = 'none'
            self.norm.layout.display = 'inline'
            self.norm_flat.layout.display = 'none'
        elif self.src_select.value == "Sersic (Effective Radius)":
            self.major.layout.display = 'inline'
            self.minor.layout.display = 'inline'
            self.pos_a.layout.display = 'inline'
            self.sersic.layout.display = 'inline'
            self.power.layout.display = 'none'
            self.r_core.layout.display = 'none'
            self.norm.layout.display = 'inline'
            self.norm_flat.layout.display = 'none'
        elif self.src_select.value == "Power Law":
            self.major.layout.display = 'none'
            self.minor.layout.display = 'none'
            self.pos_a.layout.display = 'none'
            self.sersic.layout.display = 'none'
            self.power.layout.display = 'inline'
            self.r_core.layout.display = 'inline'
            self.norm.layout.display = 'none'
            self.norm_flat.layout.display = 'none'


class InstObj(object):
    """
    An instrument/detector definition block. It's comprised of two main blocks:
    Filter and Disperser
    Advanced
    """
    def __init__(self,instrument, mode):
        self.container = widgets.VBox(width="100%", background_color="#CCCCCC")

        self.instrument = instrument
        self.instrument.set_mode(mode)
        self.instrument.get_apertures()

        self.aper_box = widgets.HBox(padding='10px', width="100%")
        self.aperture = widgets.Dropdown(description="Aperture:", options=self.instrument.apertures)
        self.aper_box.children = [self.aperture]
        self.on_aperture_change(dummy)

        self.inst_box = widgets.HBox(padding='10px', width="100%")
        self.filt = widgets.Dropdown(description="Filter:", options=self.instrument.filters)
        self.disp = widgets.Dropdown(description="Disperser:", options=self.instrument.dispersers)
        self.inst_box.children = [self.filt, self.disp]

        self.det_box = widgets.HBox(padding='10px', width="100%")
        self.ngroups = widgets.BoundedIntText(description="Groups: ", min=3, max=999, value=6, width=30)
        self.nints = widgets.BoundedIntText(description="Integrations: ", min=1, max=999, value=1, width=30)
        self.nexps = widgets.BoundedIntText(description="Exposures: ", min=1, max=999, value=1, width=30)
        self.det_box.children = [self.ngroups, self.nints, self.nexps]

        self.advanced = widgets.VBox(width="100%", background_color="#CCCCCC")
        self.readmode = widgets.Dropdown(description="Readmode:", options=self.instrument.readmodes, value='medium8')
        self.subarray = widgets.Dropdown(description="Sub-array:", options=self.instrument.subarrays, value='1024x1024')
        self.advanced.children = [self.readmode, self.subarray]

        self.advanced_drop = widgets.Accordion(children=[self.advanced])
        self.advanced_drop.set_title(0, "ADVANCED")
        self.advanced_drop.selected_index = None
        self.container.children = [self.aper_box, self.inst_box, self.det_box, self.advanced_drop]

        self.aperture.observe(self.on_aperture_change)

    def on_aperture_change(self, change):
        self.instrument.set_aperture(self.aperture.value)


class ImagingApPhotObj(object):
    """
    A strategy definition block. It's comprised of two main blocks:
    Strategy
    Advanced
    """
    def __init__(self):
        self.container = widgets.VBox(width="100%", background_color="#AAAAAA")
        strat_lab = widgets.HTML(value="<b>Imaging Aperture Photometry</b>", margin='5px')

        self.target_box = widgets.HBox(padding='10px', width="100%")
        targ_lab = widgets.HTML(value="Extraction Target: ", margin='5px')
        self.target_x = widgets.BoundedFloatText(description="X:", min=-37.5, max=37.5, value=0, width=30)
        self.target_y = widgets.BoundedFloatText(description="Y:",min=-37.5, max=37.5, value=0, width=30)
        self.target_box.children = [targ_lab, self.target_x,self.target_y]

        self.advanced = widgets.VBox(width="100%", background_color="#AAAAAA")
        self.aperture_box = widgets.HBox(padding='10px', width="100%")
        ap_lab = widgets.HTML(value="Aperture radius (arcsec): ", margin='5px')
        self.ap_size = widgets.BoundedFloatText(min=0.0, max=999.0, value=0.1, width=30)
        self.ap_size.on_trait_change(self.check_ann, 'value')
        self.aperture_box.children = [ap_lab, self.ap_size]

        self.background_box = widgets.VBox(width="100%", background_color="#AAAAAA")
        bg_lab = widgets.HTML(value="Background annulus radii (arcsec): ", margin='5px')
        self.ann_inner = widgets.BoundedFloatText(description="inner", min=0.0, max=999.0, value=0.2, width=30)
        self.ann_inner.on_trait_change(self.check_ann_inner, 'value')
        self.ann_outer = widgets.BoundedFloatText(description="outer", min=0.0, max=999.0, value=0.3, width=30)
        self.ann_outer.on_trait_change(self.check_ann_outer, 'value')
        self.background_box.children = [bg_lab, self.ann_inner, self.ann_outer]
        self.advanced.children = [self.aperture_box, self.background_box]

        self.advanced_drop = widgets.Accordion(children=[self.advanced])
        self.advanced_drop.set_title(0, "ADVANCED")
        self.advanced_drop.selected_index = None
        self.container.children = [strat_lab, self.target_box, self.advanced_drop]

    def check_ann(self, name, value):
        """
        check the background estimation annulus to make sure it's valid

        Parameters
        ----------
        name: string
            not used, but expected for on_trait_change callbacks
        """
        self.check_ann_inner(name=name, value=value)
        self.check_ann_outer(name=name, value=value)

    def check_ann_inner(self, name, value):
        if self.ann_inner.value <= self.ap_size.value:
            self.ann_inner.value = round(self.ap_size.value + 0.1, 3)
        self.check_ann_outer(name=name, value=value)

    def check_ann_outer(self, name, value):
        if self.ann_outer.value - self.ann_inner.value <= 0.1:
            self.ann_outer.value = round(self.ann_inner.value + 0.1, 3)

    def on_src_select(self, name, value):
        if value == 'point':
            self.src_form.visible = False
        else:
            self.src_form.visible = True


class SpecApPhotObj(ImagingApPhotObj):
    """
    A strategy definition block. It's comprised of two main blocks:
    Strategy
    Advanced
    """

    def __init__(self):
        style = {'description_width': 'initial'}
        self.container = widgets.VBox(width="100%", background_color="#AAAAAA")
        strat_lab = widgets.HTML(value="<b>Spectroscopic Aperture Extraction</b>", margin='5px')

        self.target_box = widgets.HBox(padding='10px', width="100%")
        targ_lab = widgets.HTML(value="Extraction Target: ", margin='5px')
        self.target_x = widgets.BoundedFloatText(description="X:", min=-37.5, max=37.5, value=0, width=30)
        self.target_y = widgets.BoundedFloatText(description="Y:", min=-37.5, max=37.5, value=0, width=30)
        self.target_box.children = [targ_lab, self.target_x, self.target_y]

        self.reference_wavelength = widgets.BoundedFloatText(description="Wavelength of Interest", min=0.95, max=1.8, value=1.3, width=30, style=style)

        self.advanced = widgets.VBox(width="100%", background_color="#AAAAAA")
        self.aperture_box = widgets.HBox(padding='10px', width="100%")
        ap_lab = widgets.HTML(value="Aperture half-height (arcsec): ", margin='5px')
        self.ap_size = widgets.BoundedFloatText(min=0.0, max=999.0, value=0.1, width=30)
        self.ap_size.on_trait_change(self.check_ann, 'value')
        self.aperture_box.children = [ap_lab, self.ap_size]

        self.background_box = widgets.VBox(width="100%", background_color="#AAAAAA")
        bg_lab = widgets.HTML(value="Sky Sample Region (arcsec): ", margin='5px')
        self.ann_inner = widgets.BoundedFloatText(description="inner", min=0.0, max=999.0, value=0.2, width=30)
        self.ann_inner.on_trait_change(self.check_ann_inner, 'value')
        self.ann_outer = widgets.BoundedFloatText(description="outer", min=0.0, max=999.0, value=0.3, width=30)
        self.ann_outer.on_trait_change(self.check_ann_outer, 'value')
        self.background_box.children = [bg_lab, self.ann_inner, self.ann_outer]
        self.advanced.children = [self.aperture_box, self.background_box]

        self.advanced_drop = widgets.Accordion(children=[self.advanced])
        self.advanced_drop.set_title(0, "ADVANCED")
        self.advanced_drop.selected_index = None
        self.container.children = [strat_lab, self.target_box, self.reference_wavelength, self.advanced_drop]


class WFIRST_gui(object):
    """
    create a basic GUI for WFIRST calculations using ipython widgets. to be run from within a jupyter notebook.
    """
    def __init__(self):
        self.r = {}
        usernotes = widgets.HTML(value="<b>If no advanced settings are changed,</b> a centered point source with no "
                                      "redshift will be computed using readmode 'medium8' and subarray '1024x1024', "
                                       "with extraction aperture centered at 0,0 with a size of 0.1 arcsec, and a sky "
                                      "annulus from 0.2-0.3 arcsec."
                                       "<p>The readout patterns are currently inherited from JWST NIRCam. To best "
                                       "approximate readouts as currently envisioned for WFIRST, we suggest using the "
                                       "following:</p>"
                                       "<ul>"
                                       "<li>Subarray '1024x1024', which has a similar frame time (2.7s) as that "
                                       "expected for the WFIRST WFI. </li>"
                                       #"<li>WFIRST does not currently anticipate resetting the detector during an "
                                       #"exposure.  Thus Integrations should be set to 1.</li>"
                                       "<li><i>To approximate the current design for the High Latitude Imaging "
                                       "Survey:</i> readmode 'medium8' with Ngroups = 6 </li>"
                                       "<li><i>To approximate the current design for the High Latitude Spectroscopic "
                                       "Survey:</i> readmode 'medium8' with Ngroups = 13</li> "
                                       "<li><i>To approximate the current design for the Exoplanet Microlensing "
                                       "Survey:</i> readmode 'shallow2' with Ngroups = 4</li")


        self.form = widgets.VBox(width="100%", background_color="#EEE")
        sourcetitle = widgets.HTML(value="<h3>SOURCES</h3>")

        self.source_form = widgets.VBox(width="100%", background_color="#EEEEEE")
        self.sources = [SourceObj()]
        self.source_form.children = [self.sources[0].container]
        self.source_form.layout.border = 'solid'

        linebreak = widgets.HTML(value="<br>")
        insttitle = widgets.HTML(value="<h3>INSTRUMENT AND DETECTOR</h3>")
        self.inst_form = widgets.HBox(padding='10px', width="100%")
        self.inst_select = widgets.Dropdown(description="Mode: ", options=['WFIRST Imager'], value='WFIRST Imager')
        self.mode_select = widgets.Dropdown(description="Mode: ", options=['Imaging', 'Grism'], value='Imaging')
        self.instrument = Instrument('wfirstimager','wfirst')
        self.instrument.get_modes()
        self.inst_form.children = [self.inst_select, self.mode_select]

        # We have to define both instruments and just hide one of them until selected; we also have to do that with the
        # strategies, and force mode, strategy list, and strategy to change when mode_select changes.
        self.mode_form = widgets.VBox(padding='10px', width="100%")
        self.mode_config = {}
        self.strat_select = {}
        mode_children = []
        mode_strat_children = []
        for mode in self.instrument.modes:
            self.instrument.set_mode(mode)
            self.mode_config[mode] = InstObj(self.instrument, mode)
            mode_children.append(self.mode_config[mode].container)
            self.strat_select[mode] = widgets.Dropdown(description="Strategy: ", options=self.instrument.strategies,
                                                 value=self.instrument.strategies[0])
            mode_strat_children.append(self.strat_select[mode])
        self.mode_form.children = tuple(mode_children)
        self.mode_form.layout.border = 'solid'
        self.mode_select.observe(self.on_mode_change)

        # create both strategies, and arrange to hide all but the one currently selected by the strat_select box
        # (of which there is one for each mode, itself selected by the value of mode_select)
        strattitle = widgets.HTML(value="<h3>EXTRACTION STRATEGY</h3>")
        self.strat_box = widgets.HBox(padding='10px', width="100%")
        self.strat_box.children = tuple(mode_strat_children)
        self.strat_form = widgets.VBox(padding='10px')
        self.strat_config = {}
        self.strat_config['imagingapphot'] = ImagingApPhotObj()
        self.strat_config['specapphot'] = SpecApPhotObj()
        strat_children = [self.strat_config['imagingapphot'].container, self.strat_config['specapphot'].container]
        self.strat_form.children = tuple(strat_children)
        self.strat_form.layout.border = 'solid'

        self.calc_button = widgets.Button(description='Calculate', width="100%", background_color="#bee2c4")
        self.calc_button.on_click(self.run_calc)

        self.result_form = widgets.VBox(padding='10px')
        self.result_form.layout.display = 'none'

        # Make all the boxes, add them to tabs. They'll be (re)populated and displayed when the calculation completes.
        self.plot2d_snr = widgets.Output()
        self.plot2d_detector = widgets.Output()
        self.plot2d_saturation = widgets.Output()
        self.plot2d_ngroups_map = widgets.Output()

        self.plot1d_flux = widgets.Output()
        self.plot1d_bg_only = widgets.Output()
        self.plot1d_sn = widgets.Output()

        self.plot2d_form = widgets.Tab(children=[self.plot2d_snr, self.plot2d_detector, self.plot2d_saturation,
                                                 self.plot2d_ngroups_map])
        self.plot2d_form.set_title(0,'SNR')
        self.plot2d_form.set_title(1,'Detector')
        self.plot2d_form.set_title(2,'Saturation')
        self.plot2d_form.set_title(3,'Groups Before Saturation')

        self.plot1d_form = widgets.Tab(children=[self.plot1d_flux, self.plot1d_bg_only, self.plot1d_sn])
        self.plot1d_form.set_title(0,'Flux')
        self.plot1d_form.set_title(1,'Background Flux Only')
        self.plot1d_form.set_title(2,'SNR')

        self.json_output = widgets.Textarea(value='', description='A JSON-formatted copy of your inputs:')

        tlab1 = widgets.HTML(value="<b>Extracted S/N: <b>", margin='5px')
        self.esn = widgets.HTML(value="0.0", margin='5px')
        tlab2 = widgets.HTML(value="       <b>Extracted Flux (e-/sec): </b>", margin='5px')
        self.eflux = widgets.HTML(value="0.0", margin='5px')
        tlab3 = widgets.HTML(value="       <b>Exposure Time (sec): <b>", margin='5px')
        self.etime = widgets.HTML(value="0.0", margin='5px')

        self.computing_notice = widgets.HTML(value="<i>Calculating... please wait.</i>", margin='5px')
        self.computing_notice.layout.display = 'none'

        self.tab_form = widgets.HBox(padding='10px', width="100%", pack='center')
        self.tab_form.children = [tlab1, self.esn, tlab2, self.eflux, tlab3, self.etime]

        self.result_form.children = [self.tab_form, self.plot2d_form, self.plot1d_form]

        self.form.children = [
            usernotes,
            sourcetitle,
            self.source_form,
            linebreak,
            insttitle,
            self.inst_form,
            self.mode_form,
            linebreak,
            strattitle,
            self.strat_box,
            self.strat_form,
            linebreak,
            self.calc_button,
            self.computing_notice,
            self.result_form
        ]

        self.on_mode_change(dummy)
        self.on_strat_change(dummy)

    def plot2d(self, plotname, unitstring):
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        t = self.r['transform']
        xmin = t['x_min']
        xmax = t['x_max']
        ymin = t['y_min']
        ymax = t['y_max']
        extent = [xmin, xmax, ymin, ymax]
        im = ax1.imshow(self.r['2d'][plotname],cmap='coolwarm', extent=extent)
        ax1.set_xlabel('arcsec')
        ax1.set_ylabel('arcsec')
        if plotname == "saturation":
            norm = matplotlib.colors.Normalize(vmin=0, vmax=2)
            im.set_norm(norm)
            c = fig.colorbar(im, ax=ax1, orientation="horizontal", label=unitstring, ticks=[0, 1, 2])
            c.ax.set_xticklabels(["None", "Partial", "Full"])
        else:
            c = fig.colorbar(im, ax=ax1, orientation="horizontal", label=unitstring)
        plt.tight_layout()
        plt.show()

    def plot1d(self, plotname, unitstring):
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        # single points (imaging, for example) need to be scatter-plotted.
        if len(self.r['1d'][plotname][0]) == 1:
            im = ax1.scatter(self.r['1d'][plotname][0], self.r['1d'][plotname][1])
        else:
            im = ax1.plot(self.r['1d'][plotname][0], self.r['1d'][plotname][1])
        ax1.set_ylabel(unitstring)
        ax1.set_xlabel('microns')
        plt.tight_layout()
        plt.show()

    def on_mode_change(self,change):
        for mode in self.mode_config:
            self.mode_config[mode].container.layout.display = 'none'
            self.strat_select[mode].layout.display = 'none'
        self.mode_config[self.mode_select.value.lower()].container.layout.display = 'inline'
        self.strat_select[self.mode_select.value.lower()].layout.display = 'inline'
        self.on_strat_change(dummy)

    def on_strat_change(self,change):
        for strat in self.strat_config:
            self.strat_config[strat].container.layout.display = 'none'
        self.strat_config[self.strat_select[self.mode_select.value.lower()].value.lower()].container.layout.display = 'inline'

    def update_plots(self):
        """
        update the 1D and 2D plots.  they're part of the same figure so have to be drawn together.  hard to do
        two independent plots in one cell in a notebook.
        """
        with self.plot2d_snr:
            self.plot2d('snr', 'S/N')
            clr = clear_output(wait=True)

        with self.plot2d_detector:
            self.plot2d('detector', 'electrons / s')
            clr = clear_output(wait=True)

        with self.plot2d_saturation:
            self.plot2d('saturation', ' ')
            clr = clear_output(wait=True)

        with self.plot2d_ngroups_map:
            self.plot2d('ngroups_map', '#')
            clr = clear_output(wait=True)

        with self.plot1d_flux:
            self.plot1d('extracted_flux', 'mJy')
            clr = clear_output(wait=True)

        with self.plot1d_bg_only:
            self.plot1d('extracted_bg_only', 'mJy')
            clr = clear_output(wait=True)

        with self.plot1d_sn:
            self.plot1d('sn', '#')
            clr = clear_output(wait=True)

        #self.json_output.value = json.dumps(self.calc_input, indent=4, separators=(',', ': '))


    @property
    def display(self):
        """
        display the GUI
        """
        display(self.form)

    @property
    def calc_results(self):
        """
        return the calculation results
        """
        return self.r

    @calc_results.setter
    def calc_results(self, r):
        self.r = r
        self.update_plots()

    def on_units_select(self, name, value):
        if value == 'abmag':
            self.flux.value = 25.0
        else:
            self.flux.value = 1.0

    def run_calc(self, b):
        # notify the user that we're calculating.
        self.computing_notice.layout.display = 'inline'
        calc_mode = self.mode_select.value.lower()
        calc_strat = self.strat_select[calc_mode].value.lower()
        c = build_default_calc("wfirst", "wfirstimager", calc_mode, method=calc_strat)
        c['configuration']['detector']['nexp'] = self.mode_config[calc_mode].nexps.value
        c['configuration']['detector']['ngroup'] = self.mode_config[calc_mode].ngroups.value
        c['configuration']['detector']['nint'] = self.mode_config[calc_mode].nints.value
        c['configuration']['detector']['readmode'] = self.mode_config[calc_mode].readmode.value
        c['configuration']['detector']['subarray'] = self.mode_config[calc_mode].subarray.value
        c['configuration']['instrument']['filter'] = self.mode_config[calc_mode].filt.value

        c['scene'] = []

        for source in self.sources:
            s = build_default_source(geometry=geom_mapping[source.src_select.value])
            if source.src_select.value == "Power":
                s['shape']['r_core'] = source.r_core.value
                s['shape']['power_index'] = source.power.value
            elif source.src_select.value == "Flat":
                s['shape']['major'] = source.major.value
                s['shape']['minor'] = source.minor.value
                s['shape']['norm_method'] = norm_mapping[source.norm_flat.value]
                s['position']['orientation'] = source.pos_a.value
            elif source.src_select.value == "2D Gaussian":
                s['shape']['major'] = source.major.value
                s['shape']['minor'] = source.minor.value
                s['shape']['norm_method'] = norm_mapping[source.norm.value]
                s['position']['orientation'] = source.pos_a.value
            elif source.src_select.value == "Sersic (Effective Radius)":
                s['shape']['major'] = source.major.value
                s['shape']['minor'] = source.minor.value
                s['shape']['norm_method'] = norm_mapping[source.norm.value]
                s['shape']['sersic_index'] = source.sersic.value
                s['position']['orientation'] = source.pos_a.value
            elif source.src_select.value == "Sersic (Scale Radius)":
                s['shape']['major'] = source.major.value
                s['shape']['minor'] = source.minor.value
                s['shape']['norm_method'] = norm_mapping[source.norm.value]
                s['shape']['sersic_index'] = source.sersic.value
                s['position']['orientation'] = source.pos_a.value
            else:
                pass

            s['position']['x_offset'] = source.pos_x.value
            s['position']['y_offset'] = source.pos_y.value

            s['spectrum']['redshift'] = source.redshift.value
            s['spectrum']['normalization']['norm_flux'] = source.flux.value
            s['spectrum']['normalization']['norm_fluxunit'] = source.funits.value
            s['spectrum']['normalization']['norm_wave'] = source.wave.value

            sed = source.sed_select.value
            if sed == "power-law":
                s['spectrum']['sed']['sed_type'] = "powerlaw"
                s['spectrum']['sed']['index'] = source.pl_index.value
            if sed == "blackbody":
                s['spectrum']['sed']['sed_type'] = "blackbody"
                s['spectrum']['sed']['temp'] = source.bb_temp.value
            if sed == "phoenix":
                s['spectrum']['sed']['sed_type'] = "phoenix"
                s['spectrum']['sed']['key'] = source.phoenix_config[source.phoenix.value]
            if sed == "extragalactic":
                s['spectrum']['sed']['sed_type'] = "brown"
                s['spectrum']['sed']['key'] = source.gal_config[source.galaxies.value]
            if sed == "star":
                s['spectrum']['sed']['sed_type'] = "hst_calspec"
                s['spectrum']['sed']['key'] = source.star_config[source.star.value]

            c['scene'].append(s)

        c['strategy']['aperture_size'] = self.strat_config[calc_strat].ap_size.value
        ann = [self.strat_config[calc_strat].ann_inner.value, self.strat_config[calc_strat].ann_outer.value]
        c['strategy']['sky_annulus'] = ann
        if calc_strat == 'specapphot':
            c['strategy']['reference_wavelength'] = self.strat_config[calc_strat].reference_wavelength.value

        self.r = perform_calculation(c, dict_report=True)
        self.calc_input = c
        self.esn.value = "%.2f" % self.r['scalar']['sn']
        self.eflux.value = "%.2f" % self.r['scalar']['extracted_flux']
        self.etime.value = "%.2f" % self.r['scalar']['total_exposure_time']

        self.update_plots()
        # Now set the result form to be shown
        self.computing_notice.layout.display = 'none'
        self.result_form.layout.display = 'inline'
