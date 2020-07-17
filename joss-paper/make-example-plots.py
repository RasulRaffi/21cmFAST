"""Run the example in the JOSS paper and make plots."""
import py21cmfast as p21c

lightcone = p21c.run_lightcone(
    redshift=6.0,  # Minimum redshift of the lightcone
    max_redshift=30.0,
    user_params={
        "HII_DIM": 150,  # Number of cells along a side in the output cube
        "DIM": 400,  # Original high-resolution cell number
        "BOX_LEN": 300,  # Size of the simulation in Mpc
    },
    flag_options={
        "USE_TS_FLUCT": True,  # Do not assume saturated spin temperature
        "INHOMO_RECO": True,  # Use inhomogeneous recominations
    },
    lightcone_quantities=(  # Component fields to store as interpolated lightcones
        "brightness_temp",
        "xH_box",
        "density",
    ),
    global_quantities=(  # Component fields to store as mean values per redshift
        "xH_box",
        "brightness_temp",
    ),
)

# Save to a unique filename hashing all input parameters
lightcone.save()

# Make a lightcone sliceplot
fig = p21c.plotting.lightcone_sliceplot(lightcone, "brightness_temp")
fig.savefig("lightcone.pdf")

fig = p21c.plotting.plot_global_history(lightcone, "xH")
fig.savefig("xH_history.pdf")
