from .models import CTFVariable, CTVariable, Cmap

from library.plotting.nclcmaps import get_ncl_cmap

FIELD_KEY_SLP = "slp"
FIELD_KEY_T2 = "T2"
FIELD_KEY_TD2 = "td2"
FIELD_KEY_RH2 = "rh2"
FIELD_KEY_PREC = "rain"
FIELD_KEY_SNOW = "snow"
FIELD_KEY_WIND_10 = "wind10m"

FIELD_KEY_VORTICITY = "avo"
FIELD_KEY_GEO500 = "gh500"
FIELD_KEY_RH700 = "rh700"
FIELD_KEY_WS300 = "ws300"
FIELD_KEY_TEMP850 = "temp850"
CT_VAR_SLP = CTVariable(var_key=FIELD_KEY_SLP, title="Deniz Seviyesi Basınç", unit_text="hPa")

TEMP_COLORS = [  # reds
    "#9e0142",
    "#d53e4f",
    "#f46d43",
    "#fdae61",
    "#fee08b",
    "#ffffbf",
    "#e6f598",
    "#abdda4",
    "#66c2a5",
    "#3288bd",
    "#5e4fa2"]  # blues
TEMP_MIN = -30
TEMP_MAX = 50
TEMP_INTERVAL = 2

RH_COLORS = [
    "#ffffd9",
    "#edf8b1",
    "#c7e9b4",
    "#7fcdbb",
    "#41b6c4",
    "#1d91c0",
    "#225ea8",
    "#253494",
    "#081d58"
]
RH_MIN = 50
RH_MAX = 100
RH_INTERVAL = 5

WIND_10M_COLORS = [
    "#fff7f3",
    "#fde0dd",
    "#fcc5c0",
    "#fa9fb5",
    "#f768a1",
    "#dd3497",
    "#ae017e",
    "#7a0177",
    "#49006a",
]
WIND_10_MIN = 0.1
WIND_10_MAX = 20.1
WIND_10_INTERVAL = 2

PREC_BOUNDS = [.1, 1, 5, 10, 15, 20, 25, 30, 40, 50, 65, 80, 100, 125, 150, 175, 200, 250]

SNOW_COLORS = ["xkcd:light blue grey", "xkcd:silver", "xkcd:greyish", "xkcd:steel"]
SNOW_BOUNDS = [0.1, 1, 5, 10, 20, 30, 40, 50, 65, 80, 100]

# reverse to represent highs with reds
CMAP_T2 = Cmap(
    name="temp2m_cmap",
    ncl_cmap_name="grads_rainbow",
    type="uniform",
    vmin=TEMP_MIN,
    vmax=TEMP_MAX,
    interval=TEMP_INTERVAL)

CMAP_RH = Cmap(name="rh2m_cmap", ncl_cmap_name="MPL_YlGnBu",
               type="uniform",
               vmin=RH_MIN, vmax=RH_MAX,
               interval=RH_INTERVAL)

CMAP_WIND = Cmap(name="wind10m_cmap", ncl_cmap_name="wind_17lev",
                 type="uniform",
                 vmin=WIND_10_MIN, vmax=WIND_10_MAX,
                 interval=WIND_10_INTERVAL)

CMAP_PRECIP = Cmap(name="precip_cmap", ncl_cmap_name="precip2_16lev",
                   type="bounded", bounds=PREC_BOUNDS)

CMAP_SNOW = Cmap(name="snow_cmap", ncl_cmap_name="precip2_15lev", type="bounded", bounds=SNOW_BOUNDS)

CTF_VAR_T2 = CTFVariable(var_key=FIELD_KEY_T2, title="2m Sıcaklık", unit_text="($^{\circ}C$)", cmap=CMAP_T2)
CTF_VAR_TD2 = CTFVariable(var_key=FIELD_KEY_TD2, title="2m Çiy Noktası Sıcaklığı", unit_text="($^{\circ}C$)",
                          cmap=CMAP_T2)
CTF_VAR_RH2 = CTFVariable(var_key=FIELD_KEY_RH2, title="2m Bağıl Nem", unit_text="(%)", cmap=CMAP_RH)
CTF_VAR_WIND10 = CTFVariable(var_key=FIELD_KEY_WIND_10, title="10m rüzgar hızı", unit_text="(m/s)", cmap=CMAP_WIND)

CTF_VAR_RAIN = CTFVariable(var_key=FIELD_KEY_PREC, title="Yağış", unit_text="(mm)", cmap=CMAP_PRECIP)
CTF_VAR_SNOW = CTFVariable(var_key=FIELD_KEY_SNOW, title="Kar yağışı", unit_text="(mm)", cmap=CMAP_SNOW)

SURFACE_PLOT_VARIABLES = {
    FIELD_KEY_T2: CTF_VAR_T2,
    FIELD_KEY_TD2: CTF_VAR_TD2,
    FIELD_KEY_RH2: CTF_VAR_RH2,
    FIELD_KEY_WIND_10: CTF_VAR_WIND10,
    FIELD_KEY_PREC: CTF_VAR_RAIN,
    FIELD_KEY_SNOW: CTF_VAR_SNOW,
}


def get_contourf_variable(key: str) -> CTFVariable:
    return SURFACE_PLOT_VARIABLES.get(key)
