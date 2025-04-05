import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import numpy_financial as npf
from pandas.core.strings.accessor import cat_core

nf = "{:.0f}"
nfp = "{:.0f}"

einspeiseverguetung_ve = 11.5 # [ct/kWh]
einspeiseverguetung_ue = 8.0 # [ct/kWh]
mieterstromzuschlag = 2.5 # [ct/kWh]

st.title(':sunny: Solar für _Wohnungs-eigentümergemeinschaften_')
st.markdown('Ihr seid eine WEG und wollt eine Solaranlage bauen, wisst aber nicht ob das für euch Sinn macht oder wie das geht? Dann seid ihr hier richtig! :smile: Mit diesem einfachen Rechner könnte ihr zügig analysieren ob eine Solaranlage für euch Sinn macht. Los geht''s... :sun_with_face: ')

st.badge("ACHTUNG! Dies ist aktuell nur ein Prototyp mit begrenzter Funktionsfähigkeit.", color="red")
st.badge("Einiges funktioniert noch nicht (Schätzung Solar-Output, Rechnung Eigenverbrauch und Weiteres)", color="red")
st.badge("Einige Funktion fehlen und sollen noch kommen (z.B. ""Export als Beschlußvorlage"")", color="red")
st.badge("Vieles ist noch nicht abschließend sauber geprüft (im Prinzip alles :smile:)", color="red")
st.badge("Schreibt mir gerne Ideen und Feedback: t.p.richert@gmail.com.", color="red")

#st.sidebar.button('Einführung')
#st.sidebar.button('Haus und Solaranlage')
#st.sidebar.button('Konzeptvergleich')
#st.sidebar.button('So geht''s weiter')


st.header('Euer Haus', anchor='haus')
number_apartments = st.number_input('Anzahl der Wohnungen in eurem Haus:', min_value=0, max_value=50, value=14, key='we')
power_consumption_per_apartment = st.number_input('Stromverbrauch pro Wohnung im Jahr [kWh] (im Schnitt könnt ihr im Mehrfamilienhaus von ca. 2500 kWh/Jahr pro Haushalt ausgehen. Singles natürlich etwas weniger, Familien etwas mehr.)', min_value=0, max_value=10000, value=2500, key='stromverbrauch')
number_meters = number_apartments + 1

power_price = st.number_input('Mittlerer Strompreis mit eurem Stromversorgungsvertrag [ct/kWh]:', min_value=20, max_value=40, value=32, key='power_price')
power_base_price = st.number_input('Mittlere monatliche Grundgebühr pro Wohnung für eure Stromversorgungsverträge [EUR/Monat]:', min_value=10, max_value=30, value=20, key='power_base_price')

power_consumption = number_apartments * power_consumption_per_apartment * 1.1 # [kWh]
cost_power_annual = power_consumption * power_price / 100 + 12 * number_meters * power_base_price

st.write('Ihr verbraucht in eurem Haus ca. __' + str(nf.format(power_consumption)) + ' kWh__ Strom pro Jahr (inklusive zusätzlich ca. 10% für den Allgemeinstrom). Dafür bezahlt ihr mit Grundgebühren und Arbeitspreis __ca. ' + str(nf.format(cost_power_annual)) + ' EUR__ im Jahr.')

st.header('Eure zukünftige Photovoltaik-Anlage', anchor='anlage')

st.number_input('Postleitzahl (zur Abschätzung der Sonneneinstrahlung)', min_value=0, max_value=99999, key='plz')
capacity_kWp = st.number_input('Kapazität der Anlage [kWp]', min_value=0, max_value=200, value=21, key='capacity_kWp')
st.number_input('Anstellwinkel der Anlage [Grad]', min_value=0, max_value=200, value=10, key='angle_deg', help='Bei Flachdächern wird die Anlage typischerweise mit einem Winkel von 10 bis 15 Grad installiert. Bei Spitzdächern entspricht der Winkel dem Dachwinkel.')
cost_specific = st.number_input('Spezifische Baukosten der Anlage [EUR/kWp] (typisch sind ca. 1200 bis 1400 EUR/kWp für eine Anlage ohne Speicher)', min_value=1000, max_value=1600, value=1400, key='specific_cost')
cost_total = cost_specific * capacity_kWp

pv_production = capacity_kWp * 900 # [kWh]
self_consumption_fraction = 0.5
self_consumption_total = pv_production * self_consumption_fraction
autarkiegrad = self_consumption_total / power_consumption
einspeisung_eigenverbrauch = pv_production - self_consumption_total
einspeisung_voll = pv_production

consumption_reststrom = power_consumption - self_consumption_total

st.write('Die Solaranlage kostet euch __' + str(nf.format(cost_total)) + ' EUR__ und  wird __ca. ' + str(nf.format(pv_production)) + ' kWh__ Strom pro Jahr produzieren.')
st.write('Bei eurem Jahresverbrauch, und wenn wir ein typisches Mehrfamilienhaus annehmen, werdet ihr davon ca. __' + str(nfp.format(self_consumption_fraction*100)) + '% selbst verbrauchen__ ("Eigenverbrauchsquote"), also ca. ' + str(nf.format(self_consumption_total)) + ' kWh pro Jahr. __Damit deckt ihr euren Bedarf zu ca. ' + str(nfp.format(autarkiegrad*100)) + '% ("Autkariegrad")__. Den restlichen Solarstrom, also ' + str(nf.format(einspeisung_eigenverbrauch)) + ' kWh, speist ihr in das Stromnetz ein.')
# st.write('(Die Errechnung von Eigenverbrauch und Autarkiegrad basieren auf den Methoden des [Solarrechners](https://solar.htw-berlin.de/rechner/) der [Hochschule für Technik und Wirtschaft Berlin](https://www.htw-berlin.de/))')

st.header('Nutzung des Solarstroms im Haus', anchor='nutzung')

mk = '''

Es gibt verschiedene Arten, den Strom im Haus zu nutzen. Die Nutzungsarten laufen unter dem Fachbegriff "Messkonzepte" und die drei vermutlich interessantesten Ausprägungen sind:
- **Volleinspeisung** - Es gibt nur einen Zähler an der PV-Anlage und der Strom wird bilanziell komplett ins Stromnetz eingespeist. Dafür bekommt ihr eine Einspeisevergütung. Ihr bezieht weiterhin euren gesamten Strom von euren Stromversorgern.
- **Gemeinschaftliche Gebäudeversorgung** (GGV) - Jede Wohnung wird mit einem  ["intelligenten Messsystem" bzw. iMsys](https://www.bundesnetzagentur.de/DE/Vportal/Energie/Metering/start.html) ausgestattet (landläufig auch Smart Meter genannt). Hiermit kann euer Stromverbrauch in viertelstundengenauer Auflösung gemessen werden. Mit Hilfe eines Abrechnungsdienstleisters, der diese Solarstrommengen den teilnehmenden Haushalten zurechnet, kann der Solarstrom nun den Wohnungen zugeteilt werden. Gesetzlich geregelt wird die erst seit Mitte 2024 rechtskräftige GGV durch [EnWG §42b](https://www.gesetze-im-internet.de/enwg_2005/__42a.html).
- **Mieterstrom** - Mit diesem schon etwas etablierteren Konzept kann der Strom ebenfalls in den Wohnungen genutzt werden, und trotz des Begriffes "Mieterstrom" kann dieses Konzept auch für WEGs sehr sinnvoll sein. Im Gegensatz zur GGV, bei der jeder Solarstromnutzer seinen bisherigen Stromvertrag behält, schließt die WEG (oder ein von ihr beauftrager Dienstleister, dazu unten mehr) Stromlieferverträge mit den interessierten Hausbewohnern ab. Auch für dieses Konzept braucht es die richtige Messtechnik. Traditionell wurde das Konzept häufig mit einem "physikalischen Summenzähler" gearbeitet, also mit einer Messung des Hausstromes am Hausanschlusskasten. Mittlerweile etabliert sich aber mehr und mehr der ["virtuelle Summenzähler"](https://www.sfv.de/5-fragen-virtueller-summenzaehler), der wie auch die GGV auf iMsys basiert. Mieterstrom ist im [EnWG §42a](https://www.gesetze-im-internet.de/enwg_2005/__42a.html) reguliert.

Mehr Details zu diesen und weiteren Messkonzepten findet ihr auf dieser exzellenten :heart: Website der [Energieagentur Regio Freiburg](https://energieagentur-regio-freiburg.eu/): https://energieagentur-regio-freiburg.eu/pv-mehrparteienhaus/. Im Folgenden möchten wir uns aber noch nicht in Details verfangen, sondern die drei Konzept mal direkt vergleichen! :muscle:

'''

st.markdown(mk)

st.header('Wirtschaftlichkeit', anchor='wirtschaftlichkeit')

st.subheader('Investitionskosten')
md_investment = '''Mit dem Bau einer Solaranlage tätigt ihr ein Investment, das natürlich mit Kosten verbunden ist:

- **Bau Solaranlage** - Dies umfasst den Auftrag an den von euch gewählten Fachbetrieb, der die Solaranlage bauen soll. Dies umfasst Material und Installation der Solarmodule inkl. Befestigungsmittel, Wechselrichter, Verkabelung, Anschluss an das Zählerfeld und Inbetriebnahme der Anlage.
- **Umsetzung Messkonzept** - 
- **Einrichtungspauschale Abrechnungsdienstleister** -

:warning: **HINWEIS:** In vielen älteren Häusern sind noch weitere Umbauten notwendig, die ggf. zusätzlich kosten. Dies solltet ihr von eurem Installationsbetrieb prüfen lassen.
'''
st.markdown(md_investment)

chart_investment_x = ['(1) Ohne Solar', '(2) Volleinspeisung', 'Gemeinschaftliche Gebäudeversorgung', 'Mieterstrom']
chart_investment_y_label = 'Investitionskosten [EUR]'

cat_inv_solaranlage = "Bau Solaranlage"
cost_inv_solaranlage = [0, cost_total, cost_total, cost_total]

cat_inv_abrechnung = "Einrichtungspauschale Abrechnungsdienstleister"
cost_inv_abrechnung = [0, 0, 2000, 2000]

cat_inv_messkonzept = "Umsetzung Messkonzept"
cost_inv_messkonzept = [0, 0, 100 * number_meters, 100 * number_meters]

cost_inv_total = [0, 0, 0, 0]
for i in range (0, 4):
    cost_inv_total[i] = cost_inv_solaranlage[i] + cost_inv_abrechnung[i] + cost_inv_messkonzept[i]



data_cost_investment = pd.DataFrame(
    {
        "index": [1,2,3,4],
        "Konzepte": ['Ohne Solar', 'Volleinspeisung', 'Gemeinschaftliche Gebäudeversorgung', ' Mieterstrom'],
        cat_inv_messkonzept: cost_inv_messkonzept,
        cat_inv_abrechnung: cost_inv_abrechnung,
        cat_inv_solaranlage: cost_inv_solaranlage
    }
)
st.bar_chart(data=data_cost_investment, x='Konzepte', y=['Bau Solaranlage', 'Umsetzung Messkonzept', 'Einrichtungspauschale Abrechnungsdienstleister'], y_label=chart_investment_y_label, height=500)

st.subheader('Betriebskosten und Einnahmen')
md_op = '''Im Betrieb lassen sich Ausgaben und Einnahmen der Anlage wie folgt beschreiben:

- **Grundgebühren Stromlieferverträge** - 
- **Einkauf Netzstrom und Reststrom** - 
- **Betrieb Zähler (Wohnung + Allgemeinstrom)** - 
- **Betrieb Zähler Solaranlage** - 
- **Einnahmen aus der Einspeisevergütung** - 
- **Einnahmen aus Mieterstromzuschlag** - 

Im folgenden Diagramm sind eure voraussichtlichen jährlichen Ausgaben und - als negative Werte - Einnahmen dargestellt:
'''
st.markdown(md_op)

cost_op = x = [[0 for i in range(10)] for j in range(10)]

cat_op_meters = "Betrieb Zähler (Wohnung + Allgemeinstrom)"
cost_op_meters = [0, 0, 60 * number_meters, 60 * number_meters]

cat_op_solarmeter = "Betrieb Zähler Solaranlage"
cost_op_solarmeter = [0, 100, 100, 100]

cat_op_grundgebuehr = "Grundgebühren Stromlieferverträge"
cost_op_grundgebuehr = [12 * power_base_price * number_meters, 12 * power_base_price * number_meters,
                        12 * power_base_price * number_meters, 12 * power_base_price * 1]

cat_reststrom = "Einkauf Netzstrom/Reststrom"
cost_op_reststrom = [power_consumption * power_price / 100, power_consumption * power_price / 100,
                     consumption_reststrom * power_price / 100, consumption_reststrom * power_price / 100]

cat_abrechnung = "Abrechnungsdienstleister"
cost_op_abrechnung = [0, 0, 5 * 12 * number_meters, 5 * 12 * number_meters]

cat_einnahmen_esv = "Einspeisevergütung"
cost_op_einnahmen_esv = [0, - einspeisung_voll * einspeiseverguetung_ve / 100, - einspeisung_eigenverbrauch * einspeiseverguetung_ue / 100, - einspeisung_eigenverbrauch * einspeiseverguetung_ue / 100]

cat_einnahmen_msz = "Mieterstromzuschlag"
cost_op_einnahmen_msz = [0, 0, 0, - self_consumption_total * mieterstromzuschlag / 100]



cost_op_total = [0, 0, 0, 0]
for i in range (0, 4):
    cost_op_total[i] = cost_op_meters[i] + cost_op_solarmeter[i] + cost_op_grundgebuehr[i] + cost_op_reststrom[i] + cost_op_abrechnung[i] + cost_op_einnahmen_esv[i] + cost_op_einnahmen_msz[i]

chart_op_y_label = 'Betriebskosten [EUR/a]'
data_cost_operation = pd.DataFrame(
    {
        "index": [1,2,3,4],
        "Konzepte": ['Ohne Solar', 'Volleinspeisung', 'Gemeinschaftliche Gebäudeversorgung', ' Mieterstrom'],
        cat_op_meters: cost_op_meters,
        cat_op_solarmeter: cost_op_solarmeter,
        cat_op_grundgebuehr: cost_op_grundgebuehr,
        cat_reststrom: cost_op_reststrom,
        cat_abrechnung: cost_op_abrechnung,
        cat_einnahmen_esv: cost_op_einnahmen_esv,
        cat_einnahmen_msz: cost_op_einnahmen_msz
    }
)
st.bar_chart(data=data_cost_operation, x='Konzepte', y=[cat_op_grundgebuehr, cat_reststrom, cat_op_meters, cat_op_solarmeter, cat_abrechnung, cat_einnahmen_esv, cat_einnahmen_msz], y_label=chart_op_y_label, height=500)

st.subheader('Bewertung')
st.markdown('Aus den Investitionskosten und den durch die Solaranlage reduzierten Betriebskosten sowie den Einnahmen lassen sich nun wirtschaftliche Kenngrößen herleiten. Die Rendite der Investition sieht wie folgt aus:')

payback = [0, 0, 0, 0]
irr_percent = [0, 0, 0, 0]
for i in range (1, 4):
    rel_investment_cost = cost_inv_total[i] - cost_inv_total[0]
    rel_operating_cost = cost_op_total[i] - cost_op_total[0]
    payback[i] = - rel_investment_cost / rel_operating_cost

    cashflow = [0] * 22
    cashflow[0] = -rel_investment_cost
    for a in range (1, 21 + 1):
        cashflow[a] = -rel_operating_cost

    irr_percent[i] = npf.irr(cashflow) * 100

#st.write(payback)
#st.write(irr_percent)

cat_econ_irr = 'Rendite'
chart_econ_y_label = 'Rendite [%]'
data_econ_irr = pd.DataFrame(
    {
        "Konzepte": ['Ohne Solar', 'Volleinspeisung', 'Gemeinschaftliche Gebäudeversorgung', ' Mieterstrom'],
        cat_econ_irr: irr_percent
    }
)
st.bar_chart(data=data_econ_irr, x='Konzepte', y=[cat_econ_irr], y_label=chart_econ_y_label, height=350)


st.markdown('Und wenn man Investition zu der Ersparnis an Betriebskosten ins Verhältnis setzt ergibt sich die Amortisationsdauer wie folgt:')

cat_econ_payback = 'Amortisationsdauer'
chart_econ_payback_y_label = 'Amortisationsdauer [a]'
data_econ_pb = pd.DataFrame(
    {
        "Konzepte": ['Ohne Solar', 'Volleinspeisung', 'Gemeinschaftliche Gebäudeversorgung', ' Mieterstrom'],
        cat_econ_payback: payback
    }
)
st.bar_chart(data=data_econ_pb, x='Konzepte', y=[cat_econ_payback], y_label=chart_econ_payback_y_label, height=350)

st.header('So geht es weiter...', anchor='weiter')

st.markdown('So...')

st.divider()

md_footer = '''
_Created with :heart:  in Köln-Zollstock using [Streamlit](https://streamlit.io/). Code: https://github.com/timorichert/weg-solar. Copyright 2025._
'''
st.markdown(md_footer)