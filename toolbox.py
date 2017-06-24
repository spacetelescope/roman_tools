from __future__ import division, absolute_import, print_function
import os.path
from functools import wraps

import numpy as np
import matplotlib
from matplotlib import style
from matplotlib.colors import LogNorm
from mpl_toolkits.axes_grid1 import make_axes_locatable
style.use('ggplot')
import matplotlib.pyplot as plt

from ipywidgets import widgets
from IPython.display import display, clear_output
import traitlets

from pandeia.engine.perform_calculation import perform_calculation
from pandeia.engine.io_utils import read_json, write_json
from pandeia.engine.calc_utils import build_default_calc


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

def _trait_change(func):
    @wraps(func)
    def inner(self, change):
        if change is None:
            change = {'type': 'change', 'new': None}
        if change.get('type') != 'change':
            return
        else:
            return func(self, change['new'])
    return inner

def _hide(widget):
    widget.layout.display = 'none'

def _show(widget):
    widget.layout.display = 'inherit'

def colorbar(mappable, **kwargs):
    ax = mappable.axes
    fig = ax.figure
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    return fig.colorbar(mappable, cax=cax, **kwargs)

class PandeiaWFIRSTCalculator(object):
    """
    IPyWidgets-based graphical interface to the WFIRST functionality
    in the Pandeia ETC engine
    """
    APERTURE_INCREMENT = 0.1
    APERTURE_MIN = 0.0
    APERTURE_MAX = 2.0

    def __init__(self):
        self.calculation_result = None

        self.src_select = widgets.Dropdown(
            description="Source type:",
            options=['point', 'extended'],
            value='point'
        )
        self.src_select.observe(self.on_src_select, names='value')
        self.src_form = self._build_source_form()
        self.norm_form = self._build_norm_form()
        self.sed_form = self._build_sed_form()
        self.inst_form = self._build_inst_form()
        self.det_form = self._build_det_form()
        self.strat_form = self._build_strat_form()

        self.calc_button = widgets.Button(
            description='Calculate',
            button_style='primary',
            layout={'margin': '1rem'}
        )
        self.calc_button.on_click(self.run_calc)

        self.tab_form = self._build_tab_form()
        self.plot_form = self._build_plot_form()

        self.form = widgets.VBox([
            widgets.HTML('<h3 style="text-align: center;">Pandeia-WFIRST Signal-to-Noise Ratio Calculator</h3>', layout={'margin': '1rem'}),
            widgets.VBox([
                widgets.HTML('<h4 style="margin-top: 0;">Source properties:</h4>'),
                self.src_select,
                self.src_form,
                self.norm_form,
                self.sed_form,
            ], box_style='info', layout={'margin': '1rem'}),
            widgets.HBox([
                widgets.VBox([
                    widgets.HTML('<h4 style="margin-top: 0;">Instrument properties:</h4>'),
                    self.inst_form,
                ], box_style='info', layout={'margin': '1rem', 'flex': '1'}),
                widgets.VBox([
                    widgets.HTML('<h4 style="margin-top: 0;">Readout pattern:</h4>'),
                    self.det_form,
                ], box_style='info', layout={'margin': '1rem', 'flex': '1'}),
            ]),
            widgets.VBox([
                widgets.HTML('<h4 style="margin-top: 0;">Extraction strategy:</h4>'),
                self.strat_form,
            ], box_style='info', layout={'margin': '1rem'}),
            self.calc_button,
            self.tab_form,
            self.plot_form
        ])

    def _build_source_form(self):
        self.sersic = widgets.Dropdown(
            description="Profile:",
            options=[
                "Gaussian",
                "Exponential",
                "de Vaucouleurs"
            ],
            layout={'width': '21rem'},
        )
        self.sersic_idx = {
            "Gaussian": 0.5,
            "Exponential": 1.0,
            "de Vaucouleurs": 4.0
        }
        self.ext_scale = widgets.BoundedFloatText(
            value=0.2, min=0.0, max=100.0,
            description="Scale length (arcsec):",
            layout={'width': '18rem'},
        )
        self.ellip = widgets.BoundedFloatText(
            value=0.0, min=0.0, max=1.0,
            description="Ellipticity:",
            layout={'width': '13rem'},
        )
        self.posang = widgets.BoundedFloatText(
            min=0.0, max=360.0, value=0.0,
            description="Position angle (deg):",
            layout = {'width': '18rem'},
        )
        src_form = widgets.HBox([
            self.sersic,
            self.ext_scale,
            self.ellip,
            self.posang
        ])
        _hide(src_form)
        return src_form

    def _build_norm_form(self):
        self.flux = widgets.BoundedFloatText(
            description="Source flux:",
            min=0.0, max=1.0e30, value=1.0
        )
        self.flux.layout.width = '15rem'
        self.units = widgets.Dropdown(
            value='ujy',
            options=['abmag', 'njy', 'ujy', 'mjy', 'jy'],
        )
        self.units.layout.width = '8rem'
        self.wave = widgets.BoundedFloatText(
            min=0.1, max=99999.0, value=1.5
        )
        self.wave.layout.width = '8rem'
        self.units.observe(self.on_units_select, names='value')
        return widgets.HBox([
            self.flux,
            self.units,
            widgets.Label("at", layout={'width': 'auto'}),
            self.wave,
            widgets.Label("um"),
        ])

    def _build_sed_form(self):
        self.sed_select = widgets.Dropdown(
            description="SED type: ",
            options=['power-law', 'blackbody', 'star', 'extragalactic'],
            value='power-law',
            layout={'width': '20rem'},
        )
        self.pl_index = widgets.FloatText(
            description="Index:",
            value=1.0,
            layout={'width': '14rem'},
        )
        self.bb_temp = widgets.BoundedFloatText(
            description="Temp (K):",
            min=0.0, max=99999.0, value=6500.0,
            layout={'width': '14rem'},
        )
        _hide(self.bb_temp)

        star_config_file = os.path.join(os.environ['pandeia_refdata'], 'sed', 'phoenix', 'spectra.json')
        self.star_config = get_config(star_config_file)
        self.stars = widgets.Dropdown(
            options=sorted(self.star_config.keys()),
            layout={'width': '18rem'},
        )
        _hide(self.stars)

        gal_config_file = os.path.join(os.environ['pandeia_refdata'], 'sed', 'brown', 'spectra.json')
        self.gal_config = get_config(gal_config_file)
        self.galaxies = widgets.Dropdown(
            options=sorted(self.gal_config.keys()),
            layout={'width': '26rem'},
        )
        _hide(self.galaxies)

        self.redshift = widgets.BoundedFloatText(
            description="Redshift: z=",
            min=0.0, max=99999.0, value=0.0,
            layout={'width': '14rem'},
        )

        self.sed_select.observe(self.on_sed_select, names='value')
        return widgets.HBox([
            self.sed_select, self.pl_index, self.bb_temp,
            self.stars, self.galaxies, self.redshift,
        ])

    def _build_inst_form(self):
        imager_config = read_json(os.path.join(os.environ['pandeia_refdata'], 'wfirst', 'wfirstimager', 'config.json'))
        ifu_config = read_json(os.path.join(os.environ['pandeia_refdata'], 'wfirst', 'wfirstifu', 'config.json'))

        self.inst_select = widgets.Dropdown(
            description="Instrument:",
            options=['Imager'],
            value='Imager'
        )
        im_filters = imager_config['filters']
        im_readmodes = imager_config['readmodes']
        im_subarrays = imager_config['subarrays']
        self.filt = widgets.Dropdown(
            description="Filter:",
            options=im_filters
        )
        self.readmode = widgets.Dropdown(
            description="Readmode:",
            options=im_readmodes
        )
        self.subarray = widgets.Dropdown(
            description="Sub-array:",
            options=im_subarrays,
        )
        return widgets.VBox([
            self.inst_select,
            self.filt,
            self.readmode,
            self.subarray,
        ])

    def _build_det_form(self):
        self.ngroups = widgets.BoundedIntText(
            description="Groups:",
            min=2, max=999, value=10)
        self.nints = widgets.BoundedIntText(
            description="Integrations:",
            min=1, max=999, value=1
        )
        self.nexps = widgets.BoundedIntText(
            description="Exposures:",
            min=1, max=999, value=1
        )
        return widgets.VBox([self.ngroups, self.nints, self.nexps])

    def _build_strat_form(self):
        label_width = '20rem'
        control_width = '35rem'
        ap_label = widgets.Label('Aperture radius:')
        ap_label.layout.width = label_width
        self.ap_size = widgets.FloatSlider(
            value=0.1,
            min=self.APERTURE_MIN,
            max=self.APERTURE_MAX,
            step=self.APERTURE_INCREMENT,
        )
        self.ap_size.layout.width = control_width
        self.ap_size.observe(self.check_ann, names='value')

        self.overplot = widgets.Checkbox(description="Overlay apertures?", value=True)
        self.overplot.observe(self._trigger_update_plots, names='value')

        extraction_aperture = widgets.HBox([
            ap_label,
            self.ap_size,
            widgets.Label('arcsec'),
        ])

        background_annulus_label = widgets.Label("Background annulus radii:")
        background_annulus_label.layout.width = label_width
        self.background_annulus = widgets.FloatRangeSlider(
            value=[self.ap_size.value + 0.1, self.ap_size.value + 0.2],
            min=0,
            max=2.0,
            step=self.APERTURE_INCREMENT,
        )
        self.background_annulus.layout.width = control_width
        self.background_annulus.observe(self.check_ann, 'value')
        background_estimation = widgets.HBox([
            background_annulus_label,
            self.background_annulus,
            widgets.Label("arcsec"),
        ])
        background_estimation.layout.width = '100%'

        return widgets.VBox([
            extraction_aperture,
            background_estimation,
            self.overplot
        ])

    def _build_plot_form(self):
        self.oned_plots = {
            "Input Source Flux (mJy)": "target",
            "Input Background (MJy/sr)": "bg",
            "Focal Plane Rate (e-/sec/pixel)": "fp"
        }
        self.oned_units = {
            "target": "mJy",
            "bg": "MJy/sr",
            "fp": "e-/sec/pixel"
        }
        self.twod_plots = {
            "Detector (e-/sec)": "detector",
            "S/N": "snr",
            "Saturation": "saturation"
        }
        self.twod_units = {
            "detector": "e-/sec",
            "snr": "S/N",
            "saturation": ""
        }
        self.oned_pulldown = widgets.Dropdown(
            description="1D Plot",
            options=sorted(self.oned_plots.keys()),
            value="Input Source Flux (mJy)"
        )
        self.twod_pulldown = widgets.Dropdown(
            description="2D Image",
            options=sorted(self.twod_plots.keys()),
            value="S/N"
        )
        self.oned_pulldown.observe(self._trigger_update_plots)
        self.twod_pulldown.observe(self._trigger_update_plots)

        plot_form = widgets.HBox([self.oned_pulldown, self.twod_pulldown])
        _hide(plot_form)
        return plot_form

    def _build_tab_form(self):
        self.esn = widgets.HTML("0.0")
        self.eflux = widgets.HTML("0.0")
        self.etime = widgets.HTML("0.0")

        tab_form = widgets.HBox([
            widgets.HTML("<strong>Extracted S/N:</strong>"),
            self.esn,
            widgets.HTML("<strong>Extracted Flux (e-/sec):</strong>"),
            self.eflux,
            widgets.HTML("<strong>Exposure Time (sec):</strong>"),
            self.etime
        ])
        _hide(tab_form)
        return tab_form

    @_trait_change
    def _trigger_update_plots(self, _):
        self.update_plots()

    def update_plots(self):
        """
        update the 1D and 2D plots.  they're part of the same figure so have to be drawn together.  hard to do
        two independent plots in one cell in a notebook.
        """
        if self.calculation_result is None:
            return
        oned_key = self.oned_plots[self.oned_pulldown.value]
        twod_key = self.twod_plots[self.twod_pulldown.value]
        oned_curve = self.calculation_result['1d'][oned_key]
        twod_im = self.calculation_result['2d'][twod_key]
        fig = plt.figure(figsize=(8, 3))
        ax1 = fig.add_subplot(121)
        plot = ax1.plot(oned_curve[0], oned_curve[1])
        ax1.set_xlabel(r'$\mu m$')
        ax1.set_ylabel(self.oned_units[oned_key])
        t = self.calculation_result['transform']
        xmin = t['x_min']
        xmax = t['x_max']
        ymin = t['y_min']
        ymax = t['y_max']
        extent = [xmin, xmax, ymin, ymax]
        ax2 = fig.add_subplot(122)
        ax2.set_xlabel("arcsec")
        ax2.set_ylabel("arcsec")
        # ax2.yaxis.tick_right()
        # ax2.yaxis.set_label_position("left")
        # ax2.yaxis.set_ticks_position("both")
        im = plt.imshow(twod_im, interpolation='nearest', extent=extent)
        if self.overplot.value is True:
            circles = []
            r_min, r_max = self.background_annulus.value
            circles.append(plt.Circle((0, 0), radius=self.ap_size.value, edgecolor='white', facecolor='none'))
            circles.append(plt.Circle((0, 0), radius=r_min, edgecolor='red', facecolor='none'))
            circles.append(plt.Circle((0, 0), radius=r_max, edgecolor='red', facecolor='none'))
            for c in circles:
                im.axes.add_artist(c)
        if twod_key == "saturation":
            norm = matplotlib.colors.Normalize(vmin=0, vmax=2)
            im.set_norm(norm)
            c = colorbar(im, ax=ax2, label=self.twod_units[twod_key], ticks=[0, 1, 2])
            c.ax.set_xticklabels(["None", "Partial", "Full"])
        else:
            c = colorbar(im, ax=ax2, label=self.twod_units[twod_key])
        ax2.grid(False)
        plt.show()
        clr = clear_output(wait=True)

    def display(self):
        """
        display the GUI
        """
        return display(self.form)

    @property
    def calc_results(self):
        """
        return the calculation results
        """
        return self.calculation_result

    @calc_results.setter
    def calc_results(self, r):
        self.calculation_result = r
        self.update_plots()

    @_trait_change
    def check_ann(self, _):
        """
        check the background estimation annulus to make sure it's valid
        """
        r_min, r_max = self.background_annulus.value
        if r_min <= self.ap_size.value:
            r_min = round(r_min + self.APERTURE_INCREMENT, 3)
        if r_max - r_min <= self.APERTURE_INCREMENT:
            r_max = round(r_min + self.APERTURE_INCREMENT, 3)
        if r_max > self.background_annulus.max:
            r_max = self.background_annulus.max
        if r_min >= r_max:
            r_min = r_max - self.APERTURE_INCREMENT
        self.background_annulus.value = r_min, r_max

    @_trait_change
    def on_src_select(self, value):
        if value == 'point':
            self.src_form.layout.display = 'none'
        else:
            self.src_form.layout.display = 'inherit'

    @_trait_change
    def on_units_select(self, value):
        if value == 'abmag':
            self.flux.value = 25.0
        else:
            self.flux.value = 1.0

    @_trait_change
    def on_sed_select(self, value):
        _hide(self.pl_index)
        _hide(self.bb_temp)
        _hide(self.stars)
        _hide(self.galaxies)
        if value == 'power-law':
            _show(self.pl_index)
        elif value == 'blackbody':
            _show(self.bb_temp)
        elif value == 'star':
            _show(self.stars)
        elif value == 'extragalactic':
            _show(self.galaxies)
        else:
            raise RuntimeError("SED type unknown: {}".format(value))
    def run_calc(self, b):
        c = build_default_calc("wfirst", "wfirstimager", "imaging")
        c['configuration']['detector']['nexp'] = self.nexps.value
        c['configuration']['detector']['ngroup'] = self.ngroups.value
        c['configuration']['detector']['nint'] = self.nints.value
        c['configuration']['detector']['readmode'] = self.readmode.value
        c['configuration']['detector']['subarray'] = self.subarray.value
        c['configuration']['instrument']['filter'] = self.filt.value

        src = c['scene'][0]
        if self.src_select.value == "extended":
            src['shape']['geometry'] = 'sersic'
            a = self.ext_scale.value
            e = self.ellip.value
            b = (1.0 - e) * a
            s_idx = self.sersic_idx[self.sersic.value]
            # if gaussian, convert a/b to sigma
            if s_idx == 0.5:
                a *= np.sqrt(2.0)
                b *= np.sqrt(2.0)
            src['shape']['major'] = a
            src['shape']['minor'] = b
            src['shape']['sersic_index'] = s_idx
            src['position']['orientation'] = self.posang.value

        src['spectrum']['redshift'] = self.redshift.value
        src['spectrum']['normalization']['norm_flux'] = self.flux.value
        src['spectrum']['normalization']['norm_fluxunit'] = self.units.value
        src['spectrum']['normalization']['norm_wave'] = self.wave.value

        sed = self.sed_select.value
        if sed == "power-law":
            src['spectrum']['sed']['sed_type'] = "powerlaw"
            src['spectrum']['sed']['index'] = self.pl_index.value
        if sed == "blackbody":
            src['spectrum']['sed']['sed_type'] = "blackbody"
            src['spectrum']['sed']['temp'] = self.bb_temp.value
        if sed == "star":
            src['spectrum']['sed']['sed_type'] = "phoenix"
            src['spectrum']['sed']['key'] = self.star_config[self.stars.value]
        if sed == "extragalactic":
            src['spectrum']['sed']['sed_type'] = "brown"
            src['spectrum']['sed']['key'] = self.gal_config[self.galaxies.value]

        c['strategy']['aperture_size'] = self.ap_size.value
        c['strategy']['sky_annulus'] = self.background_annulus.value

        self.calculation_result = perform_calculation(c, dict_report=True)
        self.calc_input = c
        _show(self.plot_form)
        sn_effective_wavelength, sn_ratio = self.calculation_result['1d']['sn']
        self.esn.value = "%.2f" % sn_ratio
        extracted_flux_effective_wavelength, extracted_flux = self.calculation_result['1d']['extracted_flux']
        self.eflux.value = "%.2f" % extracted_flux
        self.etime.value = "%.2f" % self.calculation_result['information']['exposure_specification']['exposure_time']
        _show(self.tab_form)

        self.update_plots()
