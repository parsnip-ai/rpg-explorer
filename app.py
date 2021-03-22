import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import base64

title = "Leveling System Explorer"
st.set_page_config(page_title=title, initial_sidebar_state="collapsed")
st.title("Leveling System Explorer")

st.markdown(
    """
#### What kind of usage behavior are we *encouraging*?

# Usage

Each plot below visualizes our current XP system in *blue* and a simulated system in *red*. Other colors are XP systems based on formulas from some games. For ease of comparison, each simulated system is scaled to a % of total earnable XP.

You can change the Progression Type below to generate a new description and simulation to get a feel for how progression changes.

You can also manually edit our current XP system level values by opening up the sidebar using the arrow on the top-left of the page. Changing these values will update all *blue* lines in each plot. You can also download this file as a csv to save changes you made.

Plots are **interactive** so you can:
- hover over each plot to look at the value at the level
- click on any of labels in each plot legend to hide/show them
- drag and zoom into areas of each plot.
"""
)

user_levels = np.array(
    [
        1,
        150,
        300,
        450,
        600,
        750,
        950,
        1150,
        1350,
        1550,
        1750,
        2050,
        2350,
        2650,
        2950,
        3250,
        3550,
        3850,
        4150,
        4450,
        4750,
        5350,
        5950,
        6550,
        7150,
        7750,
        8350,
        8950,
        9550,
        11050,
        11650,
    ]
)
dd5e_levels = np.array(
    [
        1,
        300,
        900,
        2700,
        6500,
        14000,
        23000,
        34000,
        48000,
        64000,
        85000,
        100000,
        120000,
        140000,
        165000,
        195000,
        225000,
        265000,
        305000,
        355000,
    ]
)

dd5e_levels_norm = dd5e_levels / dd5e_levels.max() * 100
dd5e_levels_norm = np.hstack(
    [dd5e_levels_norm, [np.nan] * (len(user_levels) - len(dd5e_levels_norm))]
)
user_levels_norm = user_levels / user_levels.max() * 100

st.sidebar.subheader("Max XP")
max_xp = st.sidebar.number_input(
    "This scales all other XP in current system", value=user_levels.max()
)
download_button_elem = st.sidebar.empty()
download_link_elem = st.sidebar.empty()
st.sidebar.markdown("---")
vals = []
for i, elem in enumerate(user_levels):
    vals.append(st.sidebar.number_input(f"Level {i+1}", value=elem))
vals = np.array(vals)
vals_norm = (vals / max_xp) * 100

st.markdown("### Settings")
system_type = st.selectbox("Progression Type", ["Linear", "Exponential", "Polynomial"])

default_poly = 1.5

if system_type == "Polynomial":
    theta = st.number_input(
        "Adjust growth factor (theta)",
        value=default_poly,
        min_value=1.0,
        max_value=100.0,
    )
    dd5e_on, dd3e_on, pokemon_on = (
        st.checkbox("toggle D&D 5e", False),
        st.checkbox("toggle D&D 3e", False),
        st.checkbox("toggle Pokemon", False),
    )
    st.header(f"Progression Type: {system_type}")

    """
    Polynomial progression is a popular alternative to Exponential progression. While it can have similar overall progression and rate-of-change, progression ratios look much more different and gradually taper down to 1 in later levels. Depending on the theta value, this can make a player feel "accomplished" or "overpowered" as they reach higher levels as progression will feel faster.

    """

    st.subheader("Formula")
    st.latex(
        r"""
            xp = level^{\theta}
            """
    )
elif system_type == "Exponential":
    theta = st.number_input(
        "Adjust growth factor (theta)", value=1.1, min_value=1.0, max_value=5.0
    )
    dd5e_on, dd3e_on, pokemon_on = (
        st.checkbox("toggle D&D 5e", False),
        st.checkbox("toggle D&D 3e", False),
        st.checkbox("toggle Pokemon", False),
    )
    st.header(f"Progression Type: {system_type}")

    """
    Several different games such as _Runescape_ use approximately exponential xp curves, but with low theta values (~1.1). Lower exponential values lead to _gentler progression curves_, with near constant progression ratios close to 1. This has the effect of being verying "inviting" to the player, as the next level is always "in sight." and the game doesn't "feel" much harder as the player progresses. Too low though and the game can feel very fast and too-easy.

    Higher exponential steepen the late-game leveling curve, and increase the progression ratios, making progress "feel" harder overall.
    """

    st.subheader("Formula")
    st.latex(
        r"""
            xp = \theta^{level}
            """
    )

elif system_type == "Linear":
    theta = st.number_input("Adjust growth factor (theta)", value=default_poly)
    pokemon_on, dd5e_on, dd3e_on = (
        st.checkbox("toggle D&D 5e", False),
        st.checkbox("toggle D&D 3e", False),
        st.checkbox("toggle Pokemon", False),
    )
    st.header(f"Progression Type: {system_type}")

    """
    Linear progression feels relatively constant throughout a game, but is also easily exploitable by a player.

    This exploitablility can be seen in the _total progression ratio_ (bottom most plot) which tapers off as the player levels. This means a player can progress much faster later in the game, if they constantly try to "min-max" their xp gains (i.e. going to for the biggest xp rewards).

    Theta doesn't affect the rate of progression in linear models; it just scales the values.
    """

    st.subheader("Formula")
    st.latex(
        r"""
            xp = \theta * level
            """
    )


def download_link(object_to_download, download_filename, download_link_text):
    """
    Generates a link to download the given object_to_download.

    object_to_download (str, pd.DataFrame):  The object to be downloaded.
    download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
    download_link_text (str): Text to display for download link.

    Examples:
    download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
    download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

    """
    if isinstance(object_to_download, pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    # some strings <-> bytes conversions necessary here
    b64 = base64.b64encode(object_to_download.encode()).decode()

    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'


def bpr(arr):
    "basic progression ratio"
    out = []
    for i in range(len(arr)):
        if len(arr) - 1 > i > 0:
            out.append((arr[i + 1] - arr[i]) / (arr[i] - arr[i - 1]))
    return out


def tpr(arr):
    "total progression ratio"
    out = []
    for i in range(len(arr)):
        if 0 < i < len(arr) - 1:
            out.append(arr[i + 1] / arr[i])
    return out


def make_data(system_type):

    levels = np.arange(1, 32)

    if system_type == "Linear":
        xp = theta * levels
    elif system_type == "Polynomial":
        xp = np.power(levels, theta)
    elif system_type == "Exponential":
        xp = np.power(theta, levels)

    # constant = user_levels.max() / xp.max()
    # xp *= constant
    xp = (xp / xp.max()) * 100

    dd3e = 500 * np.power(levels, 2) - (500 * levels)
    dd3e = (dd3e / dd3e.max()) * 100

    pokemon = (4 * np.power(levels, 3)) / 5
    pokemon = (pokemon / pokemon.max()) * 100

    xp_df = pd.DataFrame(
        {
            "Level": levels,
            "Current System": vals_norm,
            "Simulated": xp,
        }
    )
    if dd5e_on:
        xp_df["D&D 5e"] = dd5e_levels_norm
    if dd3e_on:
        xp_df["D&D 3e"] = dd3e
    if pokemon_on:
        xp_df["Pokemon"] = pokemon

    xp_df = xp_df.melt(id_vars=["Level"], value_name="Value", var_name="Stat")

    deriv_df = pd.DataFrame(
        {
            "Level": levels,
            "Current System": np.hstack([np.nan, np.diff(vals_norm)]),
            "Simulated": np.hstack([np.nan, np.diff(xp)]),
        }
    )
    if dd5e_on:
        deriv_df["D&D 5e"] = np.hstack([np.nan, np.diff(dd5e_levels_norm)])
    if dd3e_on:
        deriv_df["D&D 3e"] = np.hstack([np.nan, np.diff(dd3e)])
    if pokemon_on:
        deriv_df["Pokemon"] = np.hstack([np.nan, np.diff(pokemon)])

    deriv_df = deriv_df.melt(id_vars=["Level"], value_name="Value", var_name="Stat")

    bpr_ratio_df = pd.DataFrame(
        {
            "Level": levels,
            "Current System BPR": np.hstack([np.nan, bpr(vals_norm), np.nan]),
            "Simulated BPR": np.hstack([np.nan, bpr(xp), np.nan]),
        }
    )
    if dd5e_on:
        bpr_ratio_df["D&D 5e"] = np.hstack([np.nan, bpr(dd5e_levels_norm), np.nan])
    if dd3e_on:
        bpr_ratio_df["D&D 3e"] = np.hstack([np.nan, bpr(dd3e), np.nan])
    if pokemon_on:
        bpr_ratio_df["Pokemon"] = np.hstack([np.nan, bpr(pokemon), np.nan])

    bpr_ratio_df = bpr_ratio_df.melt(
        id_vars=["Level"], value_name="Value", var_name="Stat"
    )

    tpr_ratio_df = pd.DataFrame(
        {
            "Level": levels,
            "Current System TPR": np.hstack([np.nan, tpr(vals_norm), np.nan]),
            "Simulated TPR": np.hstack([np.nan, tpr(xp), np.nan]),
        }
    )
    if dd5e_on:
        tpr_ratio_df["D&D 5e"] = np.hstack([np.nan, tpr(dd5e_levels_norm), np.nan])
    if dd3e_on:
        tpr_ratio_df["D&D 3e"] = np.hstack([np.nan, tpr(dd3e), np.nan])
    if pokemon_on:
        tpr_ratio_df["Pokemon"] = np.hstack([np.nan, tpr(pokemon), np.nan])

    tpr_ratio_df = tpr_ratio_df.melt(
        id_vars=["Level"], value_name="Value", var_name="Stat"
    )

    return xp_df, deriv_df, bpr_ratio_df, tpr_ratio_df


dfs = make_data(system_type)

dl_df = (
    dfs[0]
    .query("Stat == 'Current System'")[["Level", "Value"]]
    .assign(
        Value=lambda df: df.Value.apply(
            lambda x: int(np.round(x / 100 * user_levels.max()))
        )
    )
)

if download_button_elem.button("Make csv file for edited xp"):
    tmp_download_link = download_link(
        dl_df, "current_system_xp.csv", "Click here to download"
    )
    download_link_elem.markdown(tmp_download_link, unsafe_allow_html=True)

labels = [
    "XP (% of max)",
    "XP Derivative (% change)",
    "Basic Progression Ratio",
    "Total Progression Ratio",
]
explanations = [
    """
    ### XP Progression
    This is just a user's experience at each level.
    """,
    """
    ### XP rate-of-change
    This is the rate of xp change between levels. A constant rate of change means it should take approximately the same amount of time for a user to increase their level regardless of what level they are. The steeper the curve, the takes _longer_ it takes to level up.
    """,
    """
    ### Basic Progression Ratio
    The lower the _basic progression ratio_ (BPR), the less difference between the time a player must spend to reach one level and the next, that is, the less steep the progression curve of the game.
    """,
    """
    ### Total Progression Ratio
    The _total progression ratio_ (TPR) on the other hand shows how the total XP required for a level increases. If this value is large, it implies that the total XP a player requires for a level increases significantly as the game progresses.
    """,
]


for i, (df, label, explanation) in enumerate(zip(dfs, labels, explanations)):
    f = px.line(df, x="Level", y="Value", color="Stat", height=400, width=800)
    if i > 1:
        f.update_yaxes(title=label, range=[0.5, 4])
    elif i == 0:
        f.update_yaxes(title=label, range=[-5, 105])
    else:
        f.update_yaxes(title=label, range=[-1, 20])
    st.markdown(explanation)
    st.plotly_chart(f)


with st.beta_expander("Resources", expanded=True):
    st.write(
        """
        - [Levels systems in famous RPGs](https://pavcreations.com/level-systems-and-character-growth-in-rpg-games/)
        - [Mathematics of Progression](https://onlyagame.typepad.com/only_a_game/2006/08/mathematics_of_.html)
        - [D&D and the history of leveling](http://factmyth.com/factoids/dungeons-and-dragons-was-the-first-game-to-feature-exp-and-leveling-up/)
        - [Difficulty Curves and Spikes](https://cheesewatergames.net/2016/07/31/experience-point-difficulty-curves-and-spikes/)
        """
    )

st.markdown("---")
with st.beta_expander("Preview Data Download", expanded=False):
    dl_df