import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

nf = "{:.0f}"
nfp = "{:.0f}"





st.title('Solar für _Wohnungs-eigentümergemeinschaften_')
st.markdown('Ihr seid eine WEG und wollt eine Solaranlage bauen, wisst aber nicht ob das Sinn macht oder wie das geht? :sun_with_face: Dann seid ihr hier richtig! :smile: Mit diesem einfachen Rechner könnte ihr zügig analysieren ob eine Solaranlage für euch Sinn macht. Los geht''s.. :running:')
st.divider()


st.sidebar.button('Einführung')
st.sidebar.button('Haus und Solaranlage')
st.sidebar.button('Konzeptvergleich')
st.sidebar.button('So geht''s weiter')


st.header('Euer Haus', anchor='haus')
number_apartments = st.number_input('Anzahl der Wohnungen in eurem Haus:', min_value=0, max_value=200, value=10, key='we')
power_consumption_per_apartment = st.number_input('Stromverbrauch pro Wohnung im Jahr [kWh] (im Schnitt könnt ihr im Mehrfamilienhaus von ca. 2500 kWh/Jahr pro Haushalt ausgehen. Singles natürlich etwas weniger, Familien etwas mehr.)', min_value=0, max_value=10000, value=2500, key='stromverbrauch')

power_price = st.number_input('Mittlerer Strompreis [ct/kWh]:', min_value=20, max_value=40, value=30, key='power_price')

power_consumption = number_apartments * power_consumption_per_apartment * 1.1 # [kWh]
cost_power_annual = power_consumption * power_price / 100

st.write('Ihr verbraucht in eurem Haus ca. __' + str(nf.format(power_consumption)) + ' kWh__ Strom pro Jahr (inklusive zusätzlich ca. 10% für den Allgemeinstrom). Dafür bezahlt ihr __ca. ' + str(nf.format(cost_power_annual)) + ' EUR__ im Jahr.')

st.header('Eure zukünftige Photovoltaik-Anlage', anchor='anlage')

st.number_input('Postleitzahl (zur Abschätzung der Sonneneinstrahlung)', min_value=0, max_value=99999, key='plz')
capacity_kWp = st.number_input('Kapazität der Anlage [kWp]', min_value=0, max_value=200, value=15, key='capacity_kWp')
st.number_input('Anstellwinkel der Anlage [Grad]', min_value=0, max_value=200, value=10, key='angle_deg', help='Bei Flachdächern wird die Anlage typischerweise mit einem Winkel von 10 bis 15 Grad installiert. Bei Spitzdächern entspricht der Winkel dem Dachwinkel.')
cost_specific = st.number_input('Spezifische Baukosten der Anlage [EUR/kWp] (typisch sind ca. 1000 bis 1500 EUR/kWp für eine Anlage ohne Speicher)', min_value=1000, max_value=2000, value=1500, key='specific_cost')
cost_total = cost_specific * capacity_kWp

pv_production = capacity_kWp * 900 # [kWh]
self_consumption_fraction = 0.5
self_consumption_total = pv_production * self_consumption_fraction
autarkiegrad = self_consumption_total / power_consumption
einspeisung = pv_production - self_consumption_total

st.write('Die Solaranlage kostet euch __' + str(nf.format(cost_total)) + ' EUR__ und  wird __ca. ' + str(nf.format(pv_production)) + ' kWh__ Strom pro Jahr produzieren.')
st.write('Bei eurem Jahresverbrauch, und wenn wir ein typisches Mehrfamilienhaus annehmen, werdet ihr davon ca. __' + str(nfp.format(self_consumption_fraction*100)) + '% selbst verbrauchen__ ("Eigenverbrauchsquote"), also ca. ' + str(nf.format(self_consumption_total)) + ' kWh pro Jahr. __Damit deckt ihr euren Bedarf zu ca. ' + str(nfp.format(autarkiegrad*100)) + '% ("Autkariegrad")__. Den restlichen Solarstrom, also ' + str(nf.format(einspeisung)) + ' kWh, speist ihr in das Stromnetz ein.')
st.write('(Die Errechnung von Eigenverbrauch und Autarkiegrad basieren auf den Methoden des [Solarrechners](https://solar.htw-berlin.de/rechner/) der [Hochschule für Technik und Wirtschaft Berlin](https://www.htw-berlin.de/))')

st.header('Nutzung des Solarstroms im Haus', anchor='nutzung')

mk = '''

Es gibt verschiedene Arten, den Strom im Haus zu nutzen. Die Nutzungsarten laufen unter dem Begriff "Betriebskonzepte" und die drei wichtigsten Ausprägungen sind:
- **Volleinspeisung** - Es gibt nur einen Zähler an der PV-Anlage und der Strom wird bilanziell komplett ins Stromnetz eingespeist. Dafür bekommt ihr eine Einspeisevergütung. Ihr bezieht weiterhin euren gesamten Strom von euren Stromversorgern.
- **Gemeinschaftliche Gebäudeversorgung** (GGV) - Jede Wohnung wird mit einem sogenannten Smart Meter ausgesattet (oder ganz korrekt: einem ["intelligenten Messsystem" bzw. iMsys](https://www.bundesnetzagentur.de/DE/Vportal/Energie/Metering/start.html)). So kann der Strom in viertelstundengenauer Auflösung gemessen werden. Mit Hilfe eines Abrechnungsdienstleisters, der die Solarstrommengen aufschlüsselt, kann der Solarstrom nun den Wohnungen zugeteilt werden. Gesetzlich geregelt wird die erst seit Mitte 2024 rechtskräftige GGV durch [EnWG §42b](https://www.gesetze-im-internet.de/enwg_2005/__42a.html).
- **Mieterstrom** - Auch mit diesem Konzept kann der Strom in den Wohnungen genutzt werden, und trotz dem Begriff "Mieterstrom" kann dieses Konzept auch für WEGs sehr sinnvoll sein. Im Gegensatz zur GGV, bei der jeder Solarstromnutzer seinen bisherigen Stromvertrag behält, schließt die WEG (oder ein von ihr beauftrager Dienstleister) Stromlieferverträge mit den interessierten Hausbewohnern ab. Auch für dieses Konzept braucht es die richtige Messtechnik. Traditionell wurde mit einem "physikalischen Summenzähler" gearbeitet, also mit einer Messung des Hausstromes am Hausanschlusskasten. Mittlerweile etabliert sich aber mehr und mehr der ["virtuelle Summenzähler"](https://www.sfv.de/5-fragen-virtueller-summenzaehler), der wie auch die GGV auf Smart Metern basiert. Mieterstrom gibt es schon etwas länger als die GGV und ist in [EnWG §42a](https://www.gesetze-im-internet.de/enwg_2005/__42a.html) reguliert.

Mehr Details zu diesen und weiteren Konzepten findet ihr auf dieser exzellenten :heart: Website der [Energieagentur Regio Freiburg](https://energieagentur-regio-freiburg.eu/): https://energieagentur-regio-freiburg.eu/pv-mehrparteienhaus/.

Im Folgenden möchten wir uns aber noch nicht in Details verfangen, sondern die drei Konzept mal direkt vergleichen! :muscle:

'''

st.markdown(mk)

st.header('Wirtschaftlichkeit', anchor='wirtschaftlichkeit')

st.subheader('Investitionskosten')
mk_investment = '''Mit dem Bau einer Solaranlage tätigt ihr ein Investment, das natürlich mit Kosten verbunden ist:

- **Bau Solaranlage** - Dies umfasst den Auftrag an den von euch gewählten Fachbetrieb, der die Solaranlage bauen soll. Dies umfasst Material und Installation der Solarmodule inkl. Befestigungsmittel, Wechselrichter, Verkabelung, Anschluss an das Zählerfeld und Inbetriebnahme der Anlage.
- **Umsetzung Messkonzept** - 
- **Einrichtungspauschale Abrechnungsdienstleister** - 

'''

st.markdown(mk_investment)

chart_investment_x = ['(1) Ohne Solar', '(2) Volleinspeisung', 'Gemeinschaftliche Gebäudeversorgung', 'Mieterstrom']
chart_investment_y_label = 'Investitionskosten [EUR]'


investment_data_pd = pd.DataFrame(
    {
        "index": [1,2,3,4],
        "Konzepte": ['Ohne Solar', 'Volleinspeisung', 'Gemeinschaftliche Gebäudeversorgung',
                     ' Mieterstrom'],
        "Umsetzung Messkonzept": [0, 0, 1000, 1000],
        "Einrichtungspauschale Abrechnungsdienstleister": [0, 0, 2000, 2000],
        "Bau Solaranlage": [0, cost_total, cost_total, cost_total]
    }
)
sorted_df = investment_data_pd.sort_values(by=['index'], ascending=True)
st.bar_chart(data=sorted_df, x='Konzepte', y=['Bau Solaranlage', 'Umsetzung Messkonzept', 'Einrichtungspauschale Abrechnungsdienstleister'], y_label=chart_investment_y_label, height=500)


#
# #
# investment_data_pd1 = pd.DataFrame(
#     {
#         "Konzepte": ['Ohne Solar', 'Volleinspeisung', 'Gemeinschaftliche Gebäudeversorgung', ' Mieterstrom'],
#         "Kosten": [{
#             "Umsetzung Messkonzept": 0,
#             "Einrichtungspauschale Abrechnungsdienstleister": 0,
#             "Bau Solaranlage": 0
#         },{
#             "Umsetzung Messkonzept": 0,
#             "Einrichtungspauschale Abrechnungsdienstleister": 0,
#             "Bau Solaranlage": cost_total
#         }, {
#             "Umsetzung Messkonzept": 1000,
#             "Einrichtungspauschale Abrechnungsdienstleister": 2000,
#             "Bau Solaranlage": cost_total
#         },{
#             "Umsetzung Messkonzept": 1000,
#             "Einrichtungspauschale Abrechnungsdienstleister": 2000,
#             "Bau Solaranlage": cost_total
#         }]
#     }
# )
#
# investment_data_pd3 = pd.DataFrame(
#     data=[{
#             "Id": 1,
#             "Konzept": 'Ohne Solar',
#             "Kosten": {
#                 "Umsetzung Messkonzept": 0,
#                 "Einrichtungspauschale Abrechnungsdienstleister": 0,
#                 "Bau Solaranlage": 0
#             }
#         },{
#             "Id": 2,
#             "Konzept": 'Volleinspeisung',
#             "Kosten": {
#                 "Umsetzung Messkonzept": 0,
#                 "Einrichtungspauschale Abrechnungsdienstleister": 0,
#                 "Bau Solaranlage": cost_total
#         }
#         }, {
#             "Id": 3,
#             "Konzept": 'Gemeinschaftliche Gebäudeversorgung',
#             "Kosten": {
#                 "Umsetzung Messkonzept": 1000,
#                 "Einrichtungspauschale Abrechnungsdienstleister": 2000,
#                 "Bau Solaranlage": cost_total
#                 }
#         },{
#             "Id": 4,
#             "Konzept": 'Mieterstrom',
#
#                 "Umsetzung Messkonzept": 1000,
#                 "Einrichtungspauschale Abrechnungsdienstleister": 2000,
#                 "Bau Solaranlage": cost_total
#         }
#     ]
# )
#
# investment_data_pd2 = pd.DataFrame(
#     data=[{
#             "Id": 1,
#             "Konzept": 'Ohne Solar',
#             "Umsetzung Messkonzept": 0,
#             "Einrichtungspauschale Abrechnungsdienstleister": 0,
#             "Bau Solaranlage": 0
#         },{
#             "Id": 2,
#             "Konzept": 'Volleinspeisung',
#             "Umsetzung Messkonzept": 0,
#             "Einrichtungspauschale Abrechnungsdienstleister": 0,
#             "Bau Solaranlage": cost_total
#         }, {
#             "Id": 3,
#             "Konzept": 'Gemeinschaftliche Gebäudeversorgung',
#             "Umsetzung Messkonzept": 1000,
#             "Einrichtungspauschale Abrechnungsdienstleister": 2000,
#             "Bau Solaranlage": cost_total
#         },{
#             "Id": 4,
#             "Konzept": 'Mieterstrom',
#             "Umsetzung Messkonzept": 1000,
#             "Einrichtungspauschale Abrechnungsdienstleister": 2000,
#             "Bau Solaranlage": cost_total
#     }]
# )
#
#
# c = (
#    alt.Chart(investment_data_pd2)
#    .mark_bar()
#    .encode(
#        x='Konzept',
#        y='sum(Konzept)',
#        order=alt.Order(
#            'Id',
#            sort='ascending'
#        )
#    )
# st.altair_chart(c)


st.subheader('Betriebskosten')
st.markdown('Im Betrieb unterscheiden sich die Kosten der einzelnen Konzepte.')

st.subheader('Bewertung')


st.header('So geht es weiter...', anchor='weiter')

st.markdown('So...')

st.divider()

st.markdown('_Created using [Streamlit](https://streamlit.io/) with :heart: in Köln-Zollstock. Copyright 2025._')