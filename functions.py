import streamlit as st
import altair as alt
import config as cfg

alt.renderers.set_embed_options(format_locale="de-DE", time_format_locale="de-DE")

###### FUNCTIONS ######

def eigenverbrauch(capacity_kWp, power_consumption):
    # Polynom EV, abgeleitet aus HTW-Rechner:
    # v01
    # y = 0.1411x6 - 1.0872x5 + 3.3682x4 - 5.4162x3 + 4.9424x2 - 2.7492x + 1.1003  / R^2 = 1
    # y = Eigenverbrauchsanteil / x = Größe PV-Anlage relativ zu Anlagengröße [Wp/kWh] / Polynom nur definiert für x = 0 bis 2
    # v02
    # y = 0.0085x6 - 0.1175x5 + 0.6429x4 - 1.7748x3 + 2.6424x2 - 2.171x + 1.0695 / R^2 = 0.9988
    # y = Eigenverbrauchsanteil / x = Größe PV-Anlage relativ zu Anlagengröße [Wp/kWh] / Polynom nur definiert für x = 0 bis 4

    c6 = 0.0085
    c5 = -0.1175
    c4 = 0.6429
    c3 = -1.7748
    c2 = 2.6424
    c1 = -2.171
    c0 = 1.0695
    x = capacity_kWp * 10**3 / power_consumption
    if (x == 0):
        y = 0
    elif (x > 4):
        y = 0.10
    elif (x < 0.1):
        y = 0.89
    else:
        y = c6*x**6 + c5*x**5 + c4*x**4 + c3*x**3 + c2*x**2 + c1*x + c0
    return y

def warnung(text):
    st.warning('_:warning: **HINWEIS:** ' + text + '_')

def zahlenformat(zahl, nks):
    # return locale.format("%.0f", zahl, grouping=True)
    return str("{:,." + str(nks) + "f}").format(zahl)

def calc_einspeiseverguetung(modus, capacity_kWp):
    if modus == "UE":
        ev1 = 7.94
        ev2 = 6.88
        ev3 = 5.62
        if capacity_kWp <= 10:
            ev = ev1
        elif capacity_kWp <= 40:
            ev = (10 * ev1 + (capacity_kWp - 10) * ev2) / capacity_kWp
        elif capacity_kWp <= 100:
            ev = (10 * ev1 + (40 - 10) * ev2 + (capacity_kWp - 40) * ev3) / capacity_kWp
        else:
            ev = 0
            raise Exception("Max capacity of 100 kW exceeded.")
    elif modus == "VE":
        ev1 = 12.6
        ev2 = 10.56
        if capacity_kWp <= 10:
            ev = ev1
        elif capacity_kWp <= 100:
            ev = (10 * ev1 + (capacity_kWp - 10) * ev2) / capacity_kWp
        else:
            ev = 0
            raise Exception("Max capacity of 100 kW exceeded.")
    else:
        ev = 0
        raise Exception("EV Mode unknown")
    return ev / 100

def transpose_list(matrix):
    return [[row[i] for row in matrix] for i in range(len(matrix[0]))]

def one_dim_list(two_dim):
    one_dim_list = [n for one_dim in two_dim for n in one_dim]
    return one_dim_list

def create_chart(data, metric, color, ylabel, height, show):
    chart = (
        alt.Chart(data)
        .mark_bar()
        .encode(
            x=alt.X('Konzept:N', sort=[]),
            y=alt.Y(metric + ':Q', sort=[], title=ylabel),
            color=alt.Color(color + ":N", legend=alt.Legend(orient='bottom')).scale(range=cfg.color_range)
        )
    ).configure_axisX(
        labelAngle=0,
        labelLimit=200,
        labelFontSize=12,
        labelColor='black',
        titleColor='black'
    ).configure_axisY(
        labelColor='black',
        titleColor='black'
    ).properties(
        height=height
    ).configure_legend(
        columns=2,
        labelColor='black',
        titleColor='black',
        disable=show
    )
    #if (color != None):
        # chart = alt.Chart(data).mark_bar().encode(color=alt.Color("Kategorie:N", legend=alt.Legend(orient='bottom')))

    st.altair_chart(chart)