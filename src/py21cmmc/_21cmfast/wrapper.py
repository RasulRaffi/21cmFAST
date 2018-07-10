"""
A thin python wrapper for the 21cmFAST C-code.
"""
from ._21cmfast import ffi, lib
import numpy as np
from ._utils import StructWithDefaults, OutputStruct
from astropy.cosmology import Planck15

from os import path
import yaml


# ======================================================================================================================
# PARAMETER STRUCTURES
# ======================================================================================================================
class CosmoParams(StructWithDefaults):
    """
    Cosmological parameters (with defaults) which translates to a C struct.

    Parameters
    ----------
    RANDOM_SEED : float, optional
        A seed to set the IC generator. If None, chosen from uniform distribution.

    SIGMA_8 : float, optional
        RMS mass variance (power spectrum normalisation).

    hlittle : float, optional
        H_0/100.

    OMm : float, optional
        Omega matter.

    OMb : float, optional
        Omega baryon, the baryon component.

    POWER_INDEX : float, optional
        Spectral index of the power spectrum.
    """
    ffi = ffi

    _defaults_ = dict(
        RANDOM_SEED = None,
        SIGMA_8 = 0.82,
        hlittle = Planck15.h,
        OMm = Planck15.Om0,
        OMb = Planck15.Ob0,
        POWER_INDEX = 0.97
    )

    @property
    def RANDOM_SEED(self):
        while not self._RANDOM_SEED:
            self._RANDOM_SEED = int(np.random.randint(1, 1e12))
        return self._RANDOM_SEED

    @property
    def OMl(self):
        return 1 - self.OMm

    def cosmology(self):
        return Planck15.clone(h = self.hlittle, Om0 = self.OMm, Ob0 = self.OMb)


class UserParams(StructWithDefaults):
    """
    Structure containing user parameters (with defaults).

    Parameters
    ----------
    HII_DIM : int, optional
        Number of cells for the low-res box.

    DIM : int,optional
        Number of cells for the high-res box (sampling ICs) along a principal axis. To avoid
        sampling issues, DIM should be at least 3 or 4 times HII_DIM, and an integer multiple.
        By default, it is set to 4*HII_DIM.

    BOX_LEN : float, optional
        Length of the box, in Mpc.
    """
    ffi = ffi

    _defaults_ = dict(
        BOX_LEN = 150.0,
        DIM = None,
        HII_DIM = 100,
    )

    @property
    def DIM(self):
        return self._DIM or 4 * self.HII_DIM

    @property
    def tot_fft_num_pixels(self):
        return self.DIM**3

    @property
    def HII_tot_num_pixels(self):
        return self.HII_DIM**3


class AstroParams(StructWithDefaults):
    """
    Astrophysical parameters.

    Parameters
    ----------
    INHOMO_RECO : bool, optional
    EFF_FACTOR_PL_INDEX : float, optional
    HII_EFF_FACTOR : float, optional
    R_BUBBLE_MAX : float, optional
    ION_Tvir_MIN : float, optional
    L_X : float, optional
    NU_X_THRESH : float, optional
    NU_X_BAND_MAX : float, optional
    NU_X_MAX : float, optional
    X_RAY_SPEC_INDEX : float, optional
    X_RAY_Tvir_MIN : float, optional
    X_RAY_Tvir_LOWERBOUND : float, optional
    X_RAY_Tvir_UPPERBOUND : float, optional
    F_STAR : float, optional
    t_STAR : float, optional
    N_RSD_STEPS : float, optional
    LOS_direction : int < 3, optional
    Z_HEAT_MAX : float, optional
        Maximum redshift used in the Ts.c computation. Typically fixed at z = 35,
        but can be set to lower if the user wants light-cones in the saturated
        spin temperature limit (T_S >> T_CMB)

    ZPRIME_STEP_FACTOR : float, optional
        Used to control the redshift step-size for the Ts.c integrals. Typically fixed at 1.02,
        can consider increasing to make the code faster if the user wants
        light-cones in the saturated spin temperature limit (T_S >> T_CMB)
    """
    _defaults_ = dict(
        EFF_FACTOR_PL_INDEX = 0.0,
        HII_EFF_FACTOR = 30.0,
        R_BUBBLE_MAX = None,
        ION_Tvir_MIN = 4.69897,
        L_X = 40.0,
        NU_X_THRESH = 500.0,
        NU_X_BAND_MAX = 2000.0,
        NU_X_MAX = 10000.0,
        X_RAY_SPEC_INDEX = 1.0,
        X_RAY_Tvir_MIN = None,
        X_RAY_Tvir_LOWERBOUND = 4.0,
        X_RAY_Tvir_UPPERBOUND = 6.0,
        F_STAR = 0.05,
        t_STAR = 0.5,
        N_RSD_STEPS = 20,
        LOS_direction = 2,
        Z_HEAT_MAX = 10.0,
        ZPRIME_STEP_FACTOR = 1.02,
    )

    def __init__(self, INHOMO_RECO, **kwargs):
        # TODO: should try to get inhomo_reco out of here... just needed for default of R_BUBBLE_MAX.
        self.INHOMO_RECO = INHOMO_RECO
        super().__init__(**kwargs)

    @property
    def R_BUBBLE_MAX(self):
        if not self._R_BUBBLE_MAX:
            return 50.0 if self.INHOMO_RECO else 15.0
        else:
            return self._R_BUBBLE_MAX

    @property
    def ION_Tvir_MIN(self):
        return 10 ** self._ION_Tvir_MIN

    @property
    def L_X(self):
        return 10 ** self._L_X

    @property
    def X_RAY_Tvir_MIN(self):
        return 10 ** self._X_RAY_Tvir_MIN if self._X_RAY_Tvir_MIN else self.ION_Tvir_MIN

    @property
    def NU_X_THRESH(self):
        return self._NU_X_THRESH * lib.NU_over_EV

    @property
    def NU_X_BAND_MAX(self):
        return self._NU_X_BAND_MAX * lib.NU_over_EV

    @property
    def NU_X_MAX(self):
        return self._NU_X_MAX * lib.NU_over_EV


class FlagOptions(StructWithDefaults):
    """
    Flag-style options for the ionization routines.

    Parameters
    ----------
    INCLUDE_ZETA_PL : bool, optional
        Should always be zero (have yet to include this option)

    SUBCELL_RSDS : bool, optional
        Add sub-cell RSDs (currently doesn't work if Ts is not used)

    IONISATION_FCOLL_TABLE : bool, optional
        An interpolation table for ionisation collapsed fraction (will be removing this at some point)

    USE_FCOLL_TABLE : bool, optional
        An interpolation table for ionisation collapsed fraction (for Ts.c; will be removing this at some point)

    INHOMO_RECO : bool, optional
        Whether to perform inhomogeneous recombinations
    """
    _defaults_ = dict(
        INCLUDE_ZETA_PL=False,
        SUBCELL_RSD=False,
        USE_FCOLL_IONISATION_TABLE=False,
        SHORTEN_FCOLL=False,
        INHOMO_RECO=False,
    )

    def _logic(self):
        # TODO: this needs to be discussed and fixed.
        if self.GenerateNewICs and (self.USE_FCOLL_IONISATION_TABLE or self.SHORTEN_FCOLL):
            raise ValueError(
                """
                Cannot use interpolation tables when generating new initial conditions on the fly.
                (Interpolation tables are only valid for a single cosmology/initial condition)
                """
            )

        if self.USE_TS_FLUCT and self.INCLUDE_ZETA_PL:
            raise NotImplementedError(
                """
                Cannot use a non-constant ionising efficiency (zeta) in conjuction with the IGM spin temperature part of the code.
                (This will be changed in future)
                """
            )

        if self.USE_FCOLL_IONISATION_TABLE and self.INHOMO_RECO:
            raise ValueError(
                "Cannot use the f_coll interpolation table for find_hii_bubbles with inhomogeneous recombinations")

        if self.INHOMO_RECO and self.USE_TS_FLUCT:
            raise ValueError(
                """
                Inhomogeneous recombinations have been set, but the spin temperature is not being computed.
                "Inhomogeneous recombinations can only be used in combination with the spin temperature calculation (different from 21cmFAST).
                """
            )
# ======================================================================================================================
# OUTPUT STRUCTURES
# ======================================================================================================================
class InitialConditions(OutputStruct):
    """
    A class containing all initial conditions boxes.
    """
    ffi = ffi

    def _init_boxes(self):
        self.lowres_density = np.zeros(self.user_params.HII_tot_num_pixels, dtype=np.float32)
        self.lowres_vz = np.zeros(self.user_params.HII_tot_num_pixels, dtype=np.float32)
        self.lowres_vz_2LPT = np.zeros(self.user_params.HII_tot_num_pixels, dtype=np.float32)
        self.hires_density = np.zeros(self.user_params.tot_fft_num_pixels, dtype= np.float32)
        return ['lowres_density', 'lowres_vz', 'lowre_vz_2LPT', 'hires_density']


class PerturbedField(InitialConditions):
    """
    A class containing all perturbed field boxes
    """
    _id = "InitialConditions" # Makes it look at the InitialConditions files for writing.

    def __init__(self, user_params, cosmo_params, redshift):
        super().__init__(user_params, cosmo_params, redshift=float(redshift))

        # Extend its group name to include the redshift, so that
        self._group += "_z%.4f"%self.redshift

    def _init_boxes(self):
        self.density = np.zeros(self.user_params.HII_tot_num_pixels, dtype=np.float32)
        self.velocity = np.zeros(self.user_params.HII_tot_num_pixels, dtype=np.float32)
        return ['density', 'velocity']


class IonizedBox(OutputStruct):
    def __init__(self, user_params, cosmo_params, redshift, astro_params, flag_options):
        super().__init__(user_params, cosmo_params, redshift=float(redshift), astro_params=astro_params,
                         flag_options=flag_options)

    def _init_boxes(self):
        self.ionized_box = np.zeros(self.user_params.HII_tot_num_pixels, dtype=np.float32)
        return ['ionized_box']


class TsBox(IonizedBox):
    def _init_boxes(self):
        self.Ts_box = np.zeros(self.user_params.HII_tot_num_pixels, dtype=np.float32)
        return ['Ts_box']


# ======================================================================================================================
# WRAPPING FUNCTIONS
# ======================================================================================================================
def initial_conditions(user_params=UserParams(), cosmo_params=CosmoParams(), regenerate=False, write=True, direc=None,
                       fname=None, match_seed=False):
    """
    Compute initial conditions.

    Parameters
    ----------
    user_params : `~UserParams` instance, optional
        Defines the overall options and parameters of the run.

    cosmo_params : `~CosmoParams` instance, optional
        Defines the cosmological parameters used to compute initial conditions.

    regenerate : bool, optional
        Whether to force regeneration of the initial conditions, even if a corresponding box is found.

    write : bool, optional
        Whether to write results to file.

    direc : str, optional
        The directory in which to search for the boxes and write them. By default, this is the centrally-managed
        directory, given by the ``config.yml`` in ``.21CMMC`.

    fname : str, optional
        The filename to search for/write to.

    match_seed : bool, optional
        Whether to force the random seed to also match in order to be considered a match.

    Returns
    -------
    `~InitialConditions`
        The class which contains the various boxes defining the initial conditions.
    """
    # First initialize memory for the boxes that will be returned.
    boxes = InitialConditions(user_params, cosmo_params)

    # First check whether the boxes already exist.
    if not regenerate:
        try:
            boxes.read(direc, fname, match_seed)
            print("Existing init_boxes found and read in.")
            return boxes
        except IOError:
            pass

    # Run the C code
    lib.ComputeInitialConditions(user_params(), cosmo_params(), boxes())
    boxes.filled = True

    # Optionally do stuff with the result (like writing it)
    if write:
        boxes.write(direc, fname)

    return boxes


def perturb_field(redshift, init_boxes=None, user_params=None, cosmo_params=None,
                  regenerate=False, write=True, direc=None,
                  fname=None, match_seed=False):
    """
    Compute a perturbed field at a given redshift.

    Parameters
    ----------
    redshift : float
        The redshift at which to compute the perturbed field.

    init_boxes : :class:`~InitialConditions` instance, optional
        If given, these initial conditions boxes will be used, otherwise initial conditions will be generated. If given,
        the user and cosmo params will be set from this object.

    user_params : `~UserParams` instance, optional
        Defines the overall options and parameters of the run.

    cosmo_params : `~CosmoParams` instance, optional
        Defines the cosmological parameters used to compute initial conditions.


    regenerate : bool, optional
        Whether to force regeneration of the initial conditions, even if a corresponding box is found.

    write : bool, optional
        Whether to write results to file.

    direc : str, optional
        The directory in which to search for the boxes and write them. By default, this is the centrally-managed
        directory, given by the ``config.yml`` in ``.21CMMC`.

    fname : str, optional
        The filename to search for/write to.

    match_seed : bool, optional
        Whether to force the random seed to also match in order to be considered a match.

    Returns
    -------
    :class:`~PerturbField`
        An object containing the density and velocity fields at the specified redshift.

    Examples
    --------
    The simplest method is just to give a redshift::

    >>> field = perturb_field(7.0)
    >>> print(field.density)

    Doing so will internally call the :func:`~initial_conditions` function. If initial conditions have already been
    calculated, this can be avoided by passing them:

    >>> init_boxes = initial_conditions()
    >>> field7 = perturb_field(7.0, init_boxes)
    >>> field8 = perturb_field(8.0, init_boxes)

    The user and cosmo parameter structures are by default inferred from the ``init_boxes``, so that the following is
    consistent::

    >>> init_boxes = initial_conditions(user_params= UserParams(HII_DIM=1000))
    >>> field7 = perturb_field(7.0, init_boxes)

    If ``init_boxes`` is not passed, then these parameters can be directly passed::

    >>> field7 = perturb_field(7.0, user_params=UserParams(HII_DIM=1000))

    """
    # Try setting the user/cosmo params via the init_boxes
    if init_boxes is not None:
        user_params = init_boxes.user_params
        cosmo_params = init_boxes.cosmo_params

    # Set to defaults if init_boxes wasn't provided and neither were they.
    user_params = user_params or UserParams()
    cosmo_params = cosmo_params or CosmoParams()

    # Make sure we've got computed init boxes.
    if init_boxes is None or not init_boxes.filled:
        init_boxes = initial_conditions(
            user_params, cosmo_params, regenerate=regenerate, write=write,
            direc=direc, fname=fname
        )

    # Initialize perturbed boxes.
    fields = PerturbedField(user_params, cosmo_params, redshift)

    # Check whether the boxes already exist
    if not regenerate:
        try:
            fields.read(direc, fname, match_seed=match_seed)
            print("Existing perturb_field boxes found and read in.")
            return fields
        except IOError:
            pass

    # Run the C Code
    lib.ComputePerturbField(redshift, init_boxes(), fields())
    fields.filled = True

    # Optionally do stuff with the result (like writing it)
    if write:
        fields.write(direc, fname)

    return fields


def ionize_box(astro_params=AstroParams(), flag_options=FlagOptions(),
               redshift=None, perturbed_field=None,
               init_boxes=None, cosmo_params=None, user_params=None,
               regenerate=False, write=True, direc=None,
               fname=None, match_seed=False, do_spin_temp=False):
    """
    Compute an ionized box at a given redshift.

    Parameters
    ----------
    astro_params: :class:`~AstroParams` instance, optional
        The astrophysical parameters defining the course of reionization.

    flag_options: :class:`~FlagOptions` instance, optional
        Some options passed to the reionization routine.

    redshift : float, optional
        The redshift at which to compute the ionized box. If `perturbed_field` is given, its inherent redshift
        will take precedence over this argument. If not, this argument is mandatory.

    perturbed_field : :class:`~PerturbField` instance, optional
        If given, this field will be used, otherwise it will be generated. To be generated, either `init_boxes` and
        `redshift` must be given, or `user_params`, `cosmo_params` and `redshift`.

    init_boxes : :class:`~InitialConditions` instance, optional
        If given, and `perturbed_field` *not* given, these initial conditions boxes will be used to generate the
        perturbed field, otherwise initial conditions will be generated on the fly. If given,
        the user and cosmo params will be set from this object.

    user_params : `~UserParams` instance, optional
        Defines the overall options and parameters of the run.

    cosmo_params : `~CosmoParams` instance, optional
        Defines the cosmological parameters used to compute initial conditions.

    regenerate : bool, optional
        Whether to force regeneration of the initial conditions, even if a corresponding box is found.

    write : bool, optional
        Whether to write results to file.

    direc : str, optional
        The directory in which to search for the boxes and write them. By default, this is the centrally-managed
        directory, given by the ``config.yml`` in ``.21CMMC`.

    fname : str, optional
        The filename to search for/write to.

    match_seed : bool, optional
        Whether to force the random seed to also match in order to be considered a match.

    do_spin_temp: bool, optional
        Whether to use spin temperature fluctuations in the calculations.

    Returns
    -------
    :class:`~IonizedBox` or :class:`~TsBox`
        An object containing the ionized box data.
    """
    if perturbed_field is None and redshift is None:
        raise ValueError("Either perturbed_field or redshift must be provided.")
    elif perturbed_field is not None:
        redshift = perturbed_field.redshift

    # Dynamically produce the perturbed field.
    if perturbed_field is None or not perturbed_field.filled:
        perturbed_field = perturb_field(
            redshift,init_boxes=init_boxes, user_params=user_params, cosmo_params=cosmo_params,
            regenerate=regenerate, write=write, direc=direc,
            fname=fname, match_seed=match_seed
        )

    if not do_spin_temp:
        cls = IonizedBox
    else:
        cls = TsBox

    box = cls(user_params=perturbed_field.user_params, cosmo_params=perturbed_field.cosmo_params,
              redshift=redshift, astro_params=astro_params, flag_options=flag_options)

    # Check whether the boxes already exist
    if not regenerate:
        try:
            box.read(direc, fname, match_seed=match_seed)
            print("Existing perturb_field boxes found and read in.")
            return box
        except IOError:
            pass

    # Run the C Code
    if not do_spin_temp:
        lib.ComputeIonizedBox(redshift, perturbed_field(), box())
    else:
        lib.ComputeTsBox(redshift, perturbed_field(), box())

    box.filled = True

    # Optionally do stuff with the result (like writing it)
    if write:
        box.write(direc, fname)

    return box


#
# def run_21cmfast(redshifts, box_dim=None, flag_options=None, astro_params=None, cosmo_params=None,
#                  write=True, regenerate=False, run_perturb=True, run_ionize=True, init_boxes=None,
#                  free_ps=True, progress_bar=True):
#
#     # Create structures of parameters
#     box_dim = box_dim or {}
#     flag_options = flag_options or {}
#     astro_params = astro_params or {}
#     cosmo_params = cosmo_params or {}
#
#     box_dim = BoxDim(**box_dim)
#     flag_options = FlagOptions(**flag_options)
#     astro_params = AstroParams(**astro_params)
#     cosmo_params = CosmoParams(**cosmo_params)
#
#     # Compute initial conditions, but only if they aren't passed in directly by the user.
#     if init_boxes is None:
#         init_boxes = initial_conditions(box_dim, cosmo_params, regenerate, write)
#
#     output = [init_boxes]
#
#     # Run perturb if desired
#     if run_perturb:
#         for z in redshifts:
#             perturb_fields = perturb_field(z, init_boxes, regenerate=regenerate)
#
#     # Run ionize if desired
#     if run_ionize:
#         ionized_boxes = ionize(redshifts, flag_options, astro_params)
#         output += [ionized_boxes]
#
#     return output

