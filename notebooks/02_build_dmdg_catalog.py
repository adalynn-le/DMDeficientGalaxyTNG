
import h5py
import numpy as np
import pandas as pd
from pathlib import Path



PROJECT_DIR = Path(
    r"C:\Users\adaly\OneDrive\Documents\DMDeficientGalaxyTNG-1"
)

DATA_DIR = (
    PROJECT_DIR
    / "data"
    / "TNG300-1"
    / "output"
    / "groups_099"
)

OUTPUT_DIR = PROJECT_DIR / "data"

OUTPUT_FILE = OUTPUT_DIR / "dmdg_catalog_z0.csv"



files = sorted(
    DATA_DIR.glob("fof_subhalo_tab_099.*.hdf5"),
    key=lambda p: int(p.stem.split(".")[-1])
)

print(f"Found {len(files)} group catalog files.")

if len(files) == 0:
    raise FileNotFoundError(
        f"No group catalog files found in:\n{DATA_DIR}"
    )

print(f"First file: {files[0].name}")
print(f"Last file:  {files[-1].name}")



subhalo_data = {
    "SubhaloMassInRadType": [],
    "SubhaloMassInRad": [],
    "SubhaloMassType": [],
    "SubhaloHalfmassRadType": [],
    "SubhaloLenType": [],
    "SubhaloGrNr": [],
    "SubhaloPos": [],
    "SubhaloSFR": [],
    "SubhaloVmax": [],
    "SubhaloVmaxRad": [],
    "SubhaloFlag": [],
    "SnapByType": [],
}

group_data = {
    "Group_M_Crit200": [],
    "Group_R_Crit200": [],
    "GroupFirstSub": [],
    "GroupNsubs": [],
    "GroupPos": [],
}



group_offset = 0
subhalo_offset = 0



for i, file in enumerate(files):

    print(
        f"Reading {i + 1}/{len(files)}: {file.name}"
    )

    with h5py.File(file, "r") as f:


        header = f["Header"].attrs

        n_subhalos = int(
            header["Nsubgroups_ThisFile"]
        )

        n_groups = int(
            header["Ngroups_ThisFile"]
        )

        print(
            f"    Groups: {n_groups:,} | "
            f"Subhalos: {n_subhalos:,}"
        )



        if n_subhalos > 0:

            sub = f["Subhalo"]


            subhalo_data[
                "SubhaloMassInRadType"
            ].append(
                sub["SubhaloMassInRadType"][:]
            )

            subhalo_data[
                "SubhaloMassInRad"
            ].append(
                sub["SubhaloMassInRad"][:]
            )


            subhalo_data[
                "SubhaloMassType"
            ].append(
                sub["SubhaloMassType"][:]
            )


            subhalo_data[
                "SubhaloHalfmassRadType"
            ].append(
                sub["SubhaloHalfmassRadType"][:]
            )


            subhalo_data[
                "SubhaloLenType"
            ].append(
                sub["SubhaloLenType"][:]
            )


            subhalo_data[
                "SubhaloGrNr"
            ].append(
                sub["SubhaloGrNr"][:]
            )


            subhalo_data[
                "SubhaloPos"
            ].append(
                sub["SubhaloPos"][:]
            )


            subhalo_data[
                "SubhaloSFR"
            ].append(
                sub["SubhaloSFR"][:]
            )


            subhalo_data[
                "SubhaloVmax"
            ].append(
                sub["SubhaloVmax"][:]
            )


            subhalo_data[
                "SubhaloVmaxRad"
            ].append(
                sub["SubhaloVmaxRad"][:]
            )


            subhalo_data[
                "SubhaloFlag"
            ].append(
                sub["SubhaloFlag"][:]
            )
            subhalo_data["SnapByType"].append(
                sub["SnapByType"][:]
            )


        if n_groups > 0:

            grp = f["Group"]


            group_data[
                "Group_M_Crit200"
            ].append(
                grp["Group_M_Crit200"][:]
            )


            group_data[
                "Group_R_Crit200"
            ].append(
                grp["Group_R_Crit200"][:]
            )


            group_data[
                "GroupFirstSub"
            ].append(
                grp["GroupFirstSub"][:] 
            )


            group_data[
                "GroupNsubs"
            ].append(
                grp["GroupNsubs"][:]
            )


            group_data[
                "GroupPos"
            ].append(
                grp["GroupPos"][:]
            )



    group_offset += n_groups
    subhalo_offset += n_subhalos



print("\nCombining subhalo data...")

combined_subhalo = {}

for key, arrays in subhalo_data.items():

    if len(arrays) == 0:
        raise RuntimeError(
            f"No data found for subhalo field: {key}"
        )

    combined_subhalo[key] = np.concatenate(
        arrays,
        axis=0
    )


print("Combining group data...")

combined_group = {}

for key, arrays in group_data.items():

    if len(arrays) == 0:
        raise RuntimeError(
            f"No data found for group field: {key}"
        )

    combined_group[key] = np.concatenate(
        arrays,
        axis=0
    )



n_subhalos = len(
    combined_subhalo["SubhaloMassInRad"]
)

n_groups = len(
    combined_group["Group_M_Crit200"]
)

print()
print("=" * 60)
print("COMBINED CATALOG")
print("=" * 60)

print(
    f"Total subhalos: {n_subhalos:,}"
)

print(
    f"Total groups:   {n_groups:,}"
)



df = pd.DataFrame()



df["SubhaloID"] = np.arange(
    n_subhalos,
    dtype=np.int64
)

df["GroupID"] = combined_subhalo[
    "SubhaloGrNr"
].astype(np.int64)



mass_in_rad_type = combined_subhalo[
    "SubhaloMassInRadType"
]

mass_in_rad = combined_subhalo[
    "SubhaloMassInRad"
]

dm_mass = mass_in_rad_type[:, 1]

with np.errstate(
    divide="ignore",
    invalid="ignore"
):

    f_dm = dm_mass / mass_in_rad

df["M_DM_2Rh"] = dm_mass

df["M_total_2Rh"] = mass_in_rad

df["f_DM"] = f_dm



mass_type = combined_subhalo[
    "SubhaloMassType"
]

df["M_star"] = mass_type[:, 4]



df["M_gas"] = mass_type[:, 0]



len_type = combined_subhalo[
    "SubhaloLenType"
]

df["N_gas"] = len_type[:, 0]

df["N_DM"] = len_type[:, 1]

df["N_star"] = len_type[:, 4]

df["N_BH"] = len_type[:, 3]



half_mass_rad_type = combined_subhalo[
    "SubhaloHalfmassRadType"
]

df["R_half_star"] = half_mass_rad_type[:, 4]



positions = combined_subhalo[
    "SubhaloPos"
]

df["x"] = positions[:, 0]

df["y"] = positions[:, 1]

df["z"] = positions[:, 2]



df["SFR"] = combined_subhalo[
    "SubhaloSFR"
]



df["Vmax"] = combined_subhalo[
    "SubhaloVmax"
]

df["VmaxRad"] = combined_subhalo[
    "SubhaloVmaxRad"
]



df["SubhaloFlag"] = combined_subhalo[
    "SubhaloFlag"
]



group_ids = df["GroupID"].to_numpy()

df["Host_M200c"] = combined_group[
    "Group_M_Crit200"
][group_ids]

df["Host_R200c"] = combined_group[
    "Group_R_Crit200"
][group_ids]



first_sub = combined_group[
    "GroupFirstSub"
][group_ids]

df["IsCentral"] = (
    df["SubhaloID"].to_numpy()
    == first_sub
)

df["IsSatellite"] = ~df["IsCentral"]



BOX_SIZE = 205000.0

host_positions = combined_group[
    "GroupPos"
][group_ids]

sub_positions = positions

delta = (
    sub_positions
    - host_positions
)


delta = (
    delta
    - BOX_SIZE
    * np.round(delta / BOX_SIZE)
)

distance = np.sqrt(
    np.sum(delta**2, axis=1)
)

df["DistanceToHost"] = distance



with np.errstate(
    divide="ignore",
    invalid="ignore"
):

    df["r_over_R200c"] = (
        df["DistanceToHost"]
        / df["Host_R200c"]
    )



df["DMDG_fDM_lt_0.5"] = (
    df["f_DM"] < 0.5
)



print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)

print(
    f"Total subhalos: "
    f"{len(df):,}"
)

print(
    f"Central galaxies: "
    f"{df['IsCentral'].sum():,}"
)

print(
    f"Satellite galaxies: "
    f"{df['IsSatellite'].sum():,}"
)

print(
    f"Objects with f_DM < 0.5: "
    f"{df['DMDG_fDM_lt_0.5'].sum():,}"
)

print(
    f"Median f_DM: "
    f"{df['f_DM'].median():.4f}"
)



OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

print()
print("Saving catalog...")

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"Saved to:\n{OUTPUT_FILE}"
)

print()
print("=" * 60)
print("DONE")
print("=" * 60)