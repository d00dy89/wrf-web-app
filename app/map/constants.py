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
FIELD_KEY_THICKNESS = "thickness"  # 500-1000mb thickness in meters
FIELD_KEY_RH850 = "rh850"

CT_VAR_SLP = CTVariable(var_key=FIELD_KEY_SLP, title="Deniz Seviyesi Basınç", unit_text="(hPa)", plot_interval=3)
CT_VAR_H500 = CTVariable(var_key=FIELD_KEY_GEO500, title="500 hPa Yükseklik", unit_text="(dm)", plot_interval=3)
CT_VAR_H850 = CTVariable(var_key=FIELD_KEY_TEMP850, title="850 hPa Jeopotansiyel Yükseklik", unit_text="(dm)",
                         plot_interval=3)
CT_VAR_HT700 = CTVariable(var_key=FIELD_KEY_RH700, title="700 hPa Jeopotansiyel Yükseklik", unit_text="(m)",
                          plot_interval=30)
CT_VAR_RH850 = CTVariable(var_key=FIELD_KEY_RH850, title="Bağıl Nem", unit_text="(%)", plot_interval=5)

CONTOUR_VARIABLES = {
    FIELD_KEY_GEO500: CT_VAR_H500,
    FIELD_KEY_SLP: CT_VAR_SLP,
    FIELD_KEY_THICKNESS: CT_VAR_H500,
    FIELD_KEY_TEMP850: CT_VAR_H850,
    FIELD_KEY_RH700: CT_VAR_HT700,
    FIELD_KEY_RH850: CT_VAR_RH850
}

TEMP_COLORS = [
    "#9e0142",  # reds
    "#d53e4f",
    "#f46d43",
    "#fdae61",
    "#fee08b",
    "#ffffbf",
    "#e6f598",
    "#abdda4",
    "#66c2a5",
    "#3288bd",
    "#5e4fa2"  # blues
]
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
RH_MIN = 10
RH_MAX = 100
RH_INTERVAL = 10

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
               interval=RH_INTERVAL, cbar_extend="max")

CMAP_WIND = Cmap(name="wind10m_cmap", ncl_cmap_name="wind_17lev",
                 type="uniform",
                 vmin=WIND_10_MIN, vmax=WIND_10_MAX,
                 interval=WIND_10_INTERVAL)

CMAP_PRECIP = Cmap(name="precip_cmap", ncl_cmap_name="precip2_16lev",
                   type="bounded", bounds=PREC_BOUNDS)

CMAP_SNOW = Cmap(name="snow_cmap", ncl_cmap_name="precip2_15lev", type="bounded", bounds=SNOW_BOUNDS)

# absoulute vorticity
AVO_BOUNDS = list(range(-42, 43, 2))
CMAP_AVO = Cmap(name="avo_cmap", ncl_cmap_name="BlRe", type="bounded", bounds=AVO_BOUNDS)

WS_500_MIN = 0
WS_500_MAX = 180
WS_500_INTERVAL = 10
CMAP_WS_500 = Cmap(name="wind500_cmap", ncl_cmap_name="wind_17lev",
                   type="uniform",
                   vmin=WS_500_MIN, vmax=WS_500_MAX,
                   interval=WS_500_INTERVAL)

WS_300_MIN = 0
WS_300_MAX = 180
WS_300_INTERVAL = 10
CMAP_WS_300 = Cmap(name="wind500_cmap", ncl_cmap_name="wind_17lev",
                   type="uniform",
                   vmin=WS_300_MIN, vmax=WS_300_MAX,
                   interval=WS_300_INTERVAL,
                   cbar_extend="max")

# center 540
THICKNESS_BOUNDS = list(range(480, 613, 12))
CMAP_THICKNESS = Cmap(name="thickness_cmap", ncl_cmap_name="grads_rainbow", type="bounded", bounds=THICKNESS_BOUNDS,
                      cbar_extend="both")

CMAP_TEMP850 = Cmap(name="temp850_cmap", ncl_cmap_name="grads_rainbow", type="uniform", vmin=TEMP_MIN, vmax=TEMP_MAX,
                    interval=3, cbar_extend="both")

CTF_VAR_TEMP850 = CTFVariable(var_key=FIELD_KEY_TEMP850, title="Sıcaklık", unit_text="($^{\circ}C$)", cmap=CMAP_TEMP850)
CTF_VAR_T2 = CTFVariable(var_key=FIELD_KEY_T2, title="2m Sıcaklık", unit_text="($^{\circ}C$)", cmap=CMAP_T2)
CTF_VAR_TD2 = CTFVariable(var_key=FIELD_KEY_TD2, title="2m Çiy Noktası Sıcaklığı", unit_text="($^{\circ}C$)",
                          cmap=CMAP_T2)
CTF_VAR_RH2 = CTFVariable(var_key=FIELD_KEY_RH2, title="2m Bağıl Nem", unit_text="(%)", cmap=CMAP_RH)
CTF_VAR_WIND10 = CTFVariable(var_key=FIELD_KEY_WIND_10, title="10m rüzgar hızı", unit_text="(m/s)", cmap=CMAP_WIND)

CTF_VAR_RAIN = CTFVariable(var_key=FIELD_KEY_PREC, title="Yağış", unit_text="(mm)", cmap=CMAP_PRECIP)
CTF_VAR_SNOW = CTFVariable(var_key=FIELD_KEY_SNOW, title="Kar yağışı", unit_text="(mm)", cmap=CMAP_SNOW)

CTF_VAR_AVO500 = CTFVariable(var_key=FIELD_KEY_GEO500, title="Mutlak Vorticity", unit_text="(1e-5/s)", cmap=CMAP_AVO)

CTF_VAR_WS500 = CTFVariable(var_key=FIELD_KEY_GEO500, title="500mb Rüzgar Hızı", unit_text="(km/s)", cmap=CMAP_WS_500)
CTF_VAR_WS300 = CTFVariable(var_key=FIELD_KEY_WS300, title="300mb Rüzgar Hızı", unit_text="(km/s)", cmap=CMAP_WS_300)

CTF_VAR_THICKNESS = CTFVariable(var_key=FIELD_KEY_THICKNESS, title="1000-500mb kalınlık", unit_text="(dm)",
                                cmap=CMAP_THICKNESS)
CTF_VAR_RH700 = CTFVariable(var_key=FIELD_KEY_RH700, title="Bağıl Nem", unit_text="(%)", cmap=CMAP_RH)

SURFACE_PLOT_VARIABLES = {
    FIELD_KEY_T2: CTF_VAR_T2,
    FIELD_KEY_TD2: CTF_VAR_TD2,
    FIELD_KEY_RH2: CTF_VAR_RH2,
    FIELD_KEY_WIND_10: CTF_VAR_WIND10,
    FIELD_KEY_PREC: CTF_VAR_RAIN,
    FIELD_KEY_SNOW: CTF_VAR_SNOW,
    FIELD_KEY_GEO500: CTF_VAR_AVO500,
    FIELD_KEY_THICKNESS: CTF_VAR_THICKNESS,
    FIELD_KEY_WS300: CTF_VAR_WS300,
    FIELD_KEY_TEMP850: CTF_VAR_TEMP850,
    FIELD_KEY_RH700: CTF_VAR_RH700
}


def get_contourf_variable(key: str) -> CTFVariable:
    return SURFACE_PLOT_VARIABLES.get(key)


def get_contour_variable(key: str) -> CTVariable:
    return CONTOUR_VARIABLES.get(key)
