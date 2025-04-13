import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import numpy_financial as npf
from numpy.f2py.auxfuncs import throw_error
# from pandas.core.strings.accessor import cat_core

###### PARAMETERS ######

specific_production = 900 # [kWh/kWp]

list_konzepte = ['Ohne Solar', 'Volleinspeisung', 'Gemeinschaftliche Gebäudeversorgung', ' Mieterstrom']

mieterstromzuschlag = [0, 0, 0, 2.5 / 100] # [EUR/kWh]

operating_cost_fraction = [0, 0.01, 0.01, 0.01]

email = 'info@wegsolar.de'

st.set_page_config(
    page_title="wegsolar.de | Solar für Wohnungseigentümergemeinschaften",
    page_icon="sunny"
)

###### FUNCTIONS ######

def eigenverbrauch(capacity_kWp, power_consumption):
    # Polynom EV, abgeleitet aus HTW-Rechner:
    # y = 0.1411x6 - 1.0872x5 + 3.3682x4 - 5.4162x3 + 4.9424x2 - 2.7492x + 1.1003  / R^2 = 1
    # y = Eigenverbrauchsanteil / x = Größe PV-Anlage relativ zu Anlagengröße [Wp/kWh] / Polynom nur definiert für x = 0 bis 2
    x = capacity_kWp * 10**3 / power_consumption
    if (x == 0) or (x > 2):
        y = 0
    else:
        y = 0.1411*x**6 - 1.0872*x**5 + 3.3682*x**4 - 5.4162*x**3 + 4.9424*x**2 - 2.7492*x + 1.1003
    return y

def warnung(text):
    st.markdown('_:warning: **HINWEIS:** ' + text + '_')

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
            throw_error("Max capacity of 100 kW exceeded.")
    elif modus == "VE":
        ev1 = 12.6
        ev2 = 10.56
        if capacity_kWp <= 10:
            ev = ev1
        elif capacity_kWp <= 100:
            ev = (10 * ev1 + (capacity_kWp - 10) * ev2) / capacity_kWp
        else:
            ev = 0
            throw_error("Max capacity of 100 kW exceeded.")
    else:
        ev = 0
        throw_error("EV Mode unknown")
    return ev / 100

def transpose_list(matrix):
    return [[row[i] for row in matrix] for i in range(len(matrix[0]))]

def one_dim_list(two_dim):
    one_dim_list = [n for one_dim in two_dim for n in one_dim]
    return one_dim_list


###### MAIN CONTENT ######
st.title(':sunny: Solar für _Wohnungs-eigentümergemeinschaften_')
st.markdown('Ihr seid eine WEG und wollt eine Solaranlage bauen, wisst aber nicht ob das für euch Sinn macht oder wie das geht? Dann seid ihr hier richtig! :smile: Mit diesem einfachen Rechner könnte ihr zügig analysieren ob eine Solaranlage für euch Sinn macht. Los geht''s... :sun_with_face: ')

st.badge("ACHTUNG! Dies ist aktuell nur ein Prototyp mit begrenzter Funktionsfähigkeit.", color="red")
st.badge("Einiges funktioniert noch nicht (Schätzung Solar-Output als Funktion der Modulausrichtung, etc.)", color="red")
st.badge("Vieles ist noch nicht abschließend sauber geprüft...", color="red")
st.badge("Schreibt mir gerne Ideen und Feedback: " + email + ".", color="red")

#st.sidebar.button('Einführung')
#st.sidebar.button('Haus und Solaranlage')
#st.sidebar.button('Konzeptvergleich')
#st.sidebar.button('So geht''s weiter')


st.header('Euer Haus', anchor='haus')
st.markdown('Macht hier Angaben zum Ist-Zustand bei euch in der WEG')

number_apartments = st.number_input('Anzahl der Wohnungen in eurem Haus:', min_value=0, max_value=50, value=14, key='we')
power_consumption_per_apartment = st.number_input('Stromverbrauch pro Wohnung im Jahr [kWh] (im Schnitt könnt ihr im Mehrfamilienhaus von ca. 2500 kWh/Jahr pro Haushalt ausgehen. Singles natürlich etwas weniger, Familien etwas mehr.)', min_value=0, max_value=10000, value=2500, key='stromverbrauch')
number_meters = number_apartments + 1

power_price = st.number_input('Mittlerer Strompreis mit eurem Stromversorgungsvertrag [ct/kWh]:', min_value=20, max_value=40, value=32, key='power_price')
power_base_price = st.number_input('Mittlere monatliche Grundgebühr pro Wohnung für eure Stromversorgungsverträge [EUR/Monat]:', min_value=10, max_value=30, value=20, key='power_base_price')

power_consumption_total = number_apartments * power_consumption_per_apartment * 1.1 # [kWh]
cost_power_annual = power_consumption_total * power_price / 100 + 12 * number_meters * power_base_price

st.write('Ihr verbraucht in eurem Haus ca. __' + str(zahlenformat(power_consumption_total, 0)) + ' kWh__ Strom pro Jahr (inklusive zusätzlich ca. 10% für den Allgemeinstrom). Dafür bezahlt ihr mit Grundgebühren und Arbeitspreis __ca. ' + str(zahlenformat(cost_power_annual, 0)) + ' EUR__ im Jahr.')

st.header('Eure zukünftige Photovoltaik-Anlage', anchor='anlage')
st.markdown('''
Gebt hier an, wie eure zukünftige Anlage aussehen soll.
''')

# st.number_input('Postleitzahl (zur Abschätzung der Sonneneinstrahlung)', min_value=0, max_value=99999, key='plz')
capacity_kWp = st.number_input('Kapazität der Anlage [kWp] - Auf Google Maps könnt ihr eure freie Dachfläche abschätzen. Pro freiem Quadratmeter können ca. 0.2 kWp installiert werden.', min_value=0, max_value=200, value=21, key='capacity_kWp')
warnung('Wie viel Kapazität ihr am Ende wirklich - mit Berücksichtigung von Verschattungen - sinnvoll auf dem Dach montieren könnt kann euch abschließend nur ein Fachbetrieb sagen. Hier könnt ihr aber mit einer Annahme starten.')

# st.number_input('Anstellwinkel der Anlage [Grad]', min_value=0, max_value=200, value=10, key='angle_deg', help='Bei Flachdächern wird die Anlage typischerweise mit einem Winkel von 10 bis 15 Grad installiert. Bei Spitzdächern entspricht der Winkel dem Dachwinkel.')
cost_specific = st.number_input('Spezifische Baukosten der Anlage [EUR/kWp] (typisch sind ca. 1200 bis 1400 EUR/kWp für eine Anlage ohne Speicher)', min_value=1000, max_value=1600, value=1400, key='specific_cost')
cost_total = cost_specific * capacity_kWp

pv_production = capacity_kWp * specific_production # [kWh]

einspeiseverguetung = [0, calc_einspeiseverguetung("VE", capacity_kWp), calc_einspeiseverguetung("UE", capacity_kWp), calc_einspeiseverguetung("UE", capacity_kWp)] # [EUR/kWh]
# st.write(einspeiseverguetung)

self_consumption_fraction = eigenverbrauch(capacity_kWp, power_consumption_total)
power_consumption_self = pv_production * self_consumption_fraction
autarkiegrad = power_consumption_self / power_consumption_total

einspeisung_eigenverbrauch = pv_production - power_consumption_self
einspeisung_voll = pv_production

power_consumption_reststrom = power_consumption_total - power_consumption_self

st.write('Die Solaranlage kostet euch __' + str(zahlenformat(cost_total, 0)) + ' EUR__ und  wird __ca. ' + str(zahlenformat(pv_production, 0)) + ' kWh__ Strom pro Jahr produzieren.')
st.write('Bei eurem Jahresverbrauch werdet ihr davon ca. __' + str(zahlenformat(self_consumption_fraction*100, 0)) + '% selbst verbrauchen__ ("Eigenverbrauchsquote"), also ca. ' + str(zahlenformat(power_consumption_self, 0)) + ' kWh pro Jahr. __Damit deckt ihr euren jährlichen Gesamtbedarf zu ca. ' + str(zahlenformat(autarkiegrad * 100, 0)) + '%__ ("Autkariegrad"). Den restlichen Solarstrom, also ' + str(zahlenformat(einspeisung_eigenverbrauch, 0)) + ' kWh, speist ihr in das Stromnetz ein.')
st.write('(Die Errechnung des Eigenverbrauchs basiert auf den Methoden des [Solarrechners](https://solar.htw-berlin.de/rechner/) der [Hochschule für Technik und Wirtschaft Berlin](https://www.htw-berlin.de/))')

st.header('Nutzung des Solarstroms im Haus', anchor='nutzung')

mk = '''
Es gibt verschiedene Arten, den Strom im Haus zu nutzen. Die Nutzungsarten laufen unter dem Fachbegriff "Messkonzepte" und die drei vermutlich interessantesten Ausprägungen sind:
- **Volleinspeisung** - Der Strom wird bilanziell komplett ins Stromnetz eingespeist und daher gibt nur einen Einspeisezähler an der PV-Anlage. Für den eingespeisten Strom bekommt ihr eine Einspeisevergütung. Ihr bezieht weiterhin den Strom für die Wohnungen von euren Stromversorgern.
- **Gemeinschaftliche Gebäudeversorgung** (GGV) - Jede Wohnung wird mit einem  ["intelligenten Messsystem" bzw. iMsys](https://www.bundesnetzagentur.de/DE/Vportal/Energie/Metering/start.html) ausgestattet (landläufig auch Smart Meter genannt). Hiermit kann euer Stromverbrauch in viertelstundengenauer Auflösung gemessen werden. Mit Hilfe eines Abrechnungsdienstleisters, der diese Solarstrommengen den teilnehmenden Haushalten zurechnet, kann der Solarstrom nun den Wohnungen zugeteilt werden. Gesetzlich geregelt wird die erst seit Mitte 2024 rechtskräftige GGV durch [EnWG §42b](https://www.gesetze-im-internet.de/enwg_2005/__42a.html).
- **Mieterstrom** - Mit diesem schon etwas etablierteren Konzept kann der Strom ebenfalls in den Wohnungen genutzt werden, und trotz des Begriffes "Mieterstrom" kann dieses Konzept auch für WEGs sehr sinnvoll sein. Im Gegensatz zur GGV, bei der jeder Solarstromnutzer seinen bisherigen Stromvertrag behält, schließt die WEG (oder ein von ihr beauftrager Dienstleister, dazu unten mehr) Stromlieferverträge mit den interessierten Hausbewohnern ab. Auch für dieses Konzept braucht es die richtige Messtechnik. Traditionell wurde das Konzept häufig mit einem "physikalischen Summenzähler" gearbeitet, also mit einer Messung des Hausstromes am Hausanschlusskasten. Mittlerweile etabliert sich aber mehr und mehr der ["virtuelle Summenzähler"](https://www.sfv.de/5-fragen-virtueller-summenzaehler), der wie auch die GGV auf iMsys basiert. Mieterstrom ist im [EnWG §42a](https://www.gesetze-im-internet.de/enwg_2005/__42a.html) reguliert.

Mehr Details zu diesen und weiteren Messkonzepten findet ihr auf dieser exzellenten :heart: Website der [Energieagentur Regio Freiburg](https://energieagentur-regio-freiburg.eu/): https://energieagentur-regio-freiburg.eu/pv-mehrparteienhaus/. Im Folgenden möchten wir uns aber noch nicht in Details verfangen, sondern die drei Konzept mal direkt vergleichen! :muscle:

'''

st.markdown(mk)

st.header('Wirtschaftlichkeit', anchor='wirtschaftlichkeit')

st.subheader('Investitionskosten')
md_investment = '''Mit dem Bau einer Solaranlage tätigt ihr ein Investment, das je nach Konzept mit folgenden geschätzten Kosten verbunden ist:

- **Bau Solaranlage** - Dies umfasst den Auftrag an den von euch gewählten Fachbetrieb, der die Solaranlage bauen soll. Dies umfasst Material und Installation der Solarmodule inkl. Befestigungsmittel, Wechselrichter, Verkabelung, Anschluss an das Zählerfeld und Inbetriebnahme der Anlage.
- **Umsetzung Messkonzept** - Dies umfasst den Austausch bzw. Einbau der Zähler. Das Messkonzept kann durch einen wettbewerblichen (wMSB) oder aber durch euren grundzuständigen (gMSB) Messstellenbetreiber umgesetzt werden. Der gMSB stellt für eine [vorzeitigen](## "as") Zähleraustausch bis zu 100 EUR pro Zähler in Rechnung, das ist der maximal erlaubte Betrag gemäß Solarspitzengesetz und hier unsere Annahme. In unserem Beispiel gehen von der Realisierung eines virtuellen Summenzählers über den gMSB aus.
- **Einrichtungspauschale Abrechnungsdienstleister** - Der Dienstleister, der euch bei der korrekten Bilanzierung und Abrechnung des Solarstroms unterstützt, verlangt eine Einrichtungspauschale und unterstützt dafür auch bei der sauberen Umsetzung des Messkonzeptes. 

'''

st.markdown(md_investment)
warnung('In manchen und insbesondere in älteren Häusern sind noch weitere Umbauten notwendig, die ggf. zusätzliche Kosten verursachen. Dies solltet ihr von einem Elektroinstallationsbetrieb prüfen lassen.')

chart_investment_x = ['Ohne Solar', 'Volleinspeisung', 'Gemeinschaftliche Gebäudeversorgung', 'Mieterstrom']
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

chart_inv_data = pd.DataFrame({'Konzept': ['Ohne Solar', 'Ohne Solar', 'Ohne Solar',
                                                'Volleinspeisung','Volleinspeisung','Volleinspeisung',
                                                'Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung',
                                                'Mieterstrom','Mieterstrom','Mieterstrom'],
                                    'Kategorie': ['Bau Solaranlage', 'Umsetzung Messkonzept', 'Einrichtungspauschale Abrechnungsdienstleister',
                                                'Bau Solaranlage', 'Umsetzung Messkonzept', 'Einrichtungspauschale Abrechnungsdienstleister',
                                                'Bau Solaranlage', 'Umsetzung Messkonzept', 'Einrichtungspauschale Abrechnungsdienstleister',
                                                'Bau Solaranlage', 'Umsetzung Messkonzept', 'Einrichtungspauschale Abrechnungsdienstleister'],
                                    'Kosten': [0, 0, 0,
                                               cost_total, 0, 0,
                                               cost_total, 1000, 2000,
                                               cost_total, 1000, 2000]})

alt.renderers.set_embed_options(format_locale="de-DE", time_format_locale="de-DE")
chart_inv = (
   alt.Chart(chart_inv_data)
   .mark_bar()
   .encode(
       x=alt.X('Konzept:N', sort=[]),
       y=alt.Y('Kosten:Q', sort=[], title='Investitionskosten [EUR]'),
       color=alt.Color("Kategorie:N", legend=alt.Legend(
           orient='bottom'))
   )
).configure_axisX(
    labelAngle=0,
    labelLimit=200,
    labelFontSize=12,
).properties(
    height=400
)
st.altair_chart(chart_inv)



st.subheader('Betriebskosten und Einnahmen')
md_op = '''Im Betrieb lassen sich Ausgaben und Einnahmen der Anlage wie folgt beschreiben:

- **Grundgebühren Stromlieferverträge** - Beim Mieterstrom habt ihr als WEG einen gemeinsamen Stromanschluss und rechnet gem. Mieterstromregeln intern ab. In allen anderen Fällen behält jeder Bewohner seinen Stromliefervertrag.
- **Einkauf Netzstrom und Reststrom** - Je nach Eigenverbrauchsquote müsste ihr bei Mieterstrom oder GGV natürlich weniger Strom einkaufen. Bei Volleinspeisung kauft ihr weiterhin sämtlichen Strom vom Stromversorger.
- **Betrieb Zähler für Wohnungen und Allgemeinstrom** - Bei Mieterstrom bezahlt ihr separat für den Betrieb der Zähler, während diese Gebühr bei Volleinspeisung und GGV, wie auch ohne Anlage, in euren Stromlieferverträgen enthalten ist.
- **Betrieb Zähler Solaranlage** - Die Solaranlage hat einen Einspeisezähler, der ebenfalls zu Buche schlägt.
- **Einnahmen aus der Einspeisevergütung** - Für den eingespeisten Solarstrom bekommt ihr eine Einspeisevergütung. Diese [errechnet sich aus der Anlagengröße](https://www.finanztip.de/photovoltaik/einspeiseverguetung/). Bei GGV und Mieterstrom gibt es eine Einspeisevergütung von ''' + str(zahlenformat(einspeiseverguetung[2] * 100, 2)) + ''' ct/kWh. Bei der Volleinspeisung gibt es einen Zuschlag und ihr bekommt so ''' + str(zahlenformat(einspeiseverguetung[1] * 100, 2)) + ''' ct/kWh.
- **Einnahmen aus Mieterstromzuschlag** - Beim Mieterstrom erhaltet für jede im Haus verbrauchte Kilowattstunde Solarstrom den Mieterstromzuschlag in Höhe von ca. 2,5 ct/kWh

Im folgenden Diagramm sind eure voraussichtlichen jährlichen Ausgaben und - als negative Werte - Einnahmen dargestellt:
'''
st.markdown(md_op)

cost_op = x = [[0 for i in range(10)] for j in range(10)]

cat_op_meters = "Betrieb Zähler (Wohnung + Allgemeinstrom)"
cost_op_meters = [0, 0, 0, 60 * number_meters]

cat_op_solarmeter = "Betrieb Zähler Solaranlage"
cost_op_solarmeter = [0, 100, 100, 100]

cat_op_grundgebuehr = "Grundgebühren Stromlieferverträge"
cost_op_grundgebuehr = [12 * power_base_price * number_meters, 12 * power_base_price * number_meters,
                        12 * power_base_price * number_meters, 12 * power_base_price * 1]

cat_reststrom = "Einkauf Netzstrom/Reststrom"
cost_op_reststrom = [power_consumption_total * power_price / 100, power_consumption_total * power_price / 100,
                     power_consumption_reststrom * power_price / 100, power_consumption_reststrom * power_price / 100]

cat_op_anlagenbetrieb = "Betrieb Solaranlage"
cost_op_anlagenbetrieb = np.multiply(cost_inv_total, operating_cost_fraction).tolist()

cat_op_abrechnung = "Abrechnungsdienstleister"
cost_op_abrechnung = [0, 0, 5 * 12 * number_meters, 5 * 12 * number_meters]

cat_op_einnahmen_esv = "Einspeisevergütung"
einspeisung = [0, -einspeisung_voll, -einspeisung_eigenverbrauch, -einspeisung_eigenverbrauch]
cost_op_einnahmen_esv = np.multiply(einspeisung, einspeiseverguetung).tolist()

cat_op_einnahmen_msz = "Mieterstromzuschlag"
eigenverbrauch = [0, 0, -power_consumption_self, -power_consumption_self]
cost_op_einnahmen_msz = np.multiply(eigenverbrauch, mieterstromzuschlag).tolist()

cost_op_total = [0, 0, 0, 0]
for i in range (0, 4):
    cost_op_total[i] = cost_op_meters[i] + cost_op_solarmeter[i] + cost_op_grundgebuehr[i] + cost_op_reststrom[i] + cost_op_anlagenbetrieb[i] + cost_op_abrechnung[i] + cost_op_einnahmen_esv[i] + cost_op_einnahmen_msz[i]

cost_op_array = one_dim_list(transpose_list([cost_op_meters, cost_op_solarmeter, cost_op_grundgebuehr, cost_op_reststrom, cost_op_anlagenbetrieb, cost_op_abrechnung, cost_op_einnahmen_esv, cost_op_einnahmen_msz]))
chart_op_data = pd.DataFrame({'Konzept': ['Ohne Solar', 'Ohne Solar', 'Ohne Solar', 'Ohne Solar', 'Ohne Solar', 'Ohne Solar', 'Ohne Solar', 'Ohne Solar',
                                                'Volleinspeisung','Volleinspeisung','Volleinspeisung','Volleinspeisung','Volleinspeisung','Volleinspeisung','Volleinspeisung','Volleinspeisung',
                                                'Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung',
                                                'Mieterstrom','Mieterstrom','Mieterstrom','Mieterstrom','Mieterstrom','Mieterstrom','Mieterstrom','Mieterstrom'],
                                    'Kategorie': [cat_op_meters, cat_op_solarmeter, cat_op_grundgebuehr, cat_reststrom, cat_op_anlagenbetrieb, cat_op_abrechnung, cat_op_einnahmen_esv, cat_op_einnahmen_msz,
                                                  cat_op_meters, cat_op_solarmeter, cat_op_grundgebuehr, cat_reststrom, cat_op_anlagenbetrieb, cat_op_abrechnung, cat_op_einnahmen_esv, cat_op_einnahmen_msz,
                                                  cat_op_meters, cat_op_solarmeter, cat_op_grundgebuehr, cat_reststrom, cat_op_anlagenbetrieb, cat_op_abrechnung, cat_op_einnahmen_esv, cat_op_einnahmen_msz,
                                                  cat_op_meters, cat_op_solarmeter, cat_op_grundgebuehr, cat_reststrom, cat_op_anlagenbetrieb, cat_op_abrechnung, cat_op_einnahmen_esv, cat_op_einnahmen_msz],
                                    'Kosten': cost_op_array})

chart_op = (
   alt.Chart(chart_op_data)
   .mark_bar()
   .encode(
       x=alt.X('Konzept:N', sort=[]),
       y=alt.Y('Kosten:Q', sort=[], title='Betriebskosten [EUR/Jahr]'),
       color=alt.Color("Kategorie:N", legend=alt.Legend(
           orient='bottom'))
   )
).configure_axisX(
    labelAngle=0,
    labelLimit=200,
    labelFontSize=12,
).properties(
    height=400
)
st.altair_chart(chart_op)

st.subheader('Bewertung')
st.markdown('Aus den Investitionskosten und den durch die Solaranlage reduzierten Betriebskosten sowie den Einnahmen lassen sich nun wirtschaftliche Kenngrößen herleiten.')

###### Calculate Economics ######

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

###### Bewertung - Rendite ######

st.markdown('Die Rendite der Investition - gerechnet über 20 Jahre - sieht wie folgt aus:')

chart_irr_data = pd.DataFrame({'Konzept': ['Ohne Solar','Volleinspeisung','Gemeinschaftliche Gebäudeversorgung','Mieterstrom'],
                                    'Rendite': irr_percent})
chart_irr = (
   alt.Chart(chart_irr_data)
   .mark_bar()
   .encode(
       x=alt.X('Konzept:N', sort=[]),
       y=alt.Y('Rendite:Q', sort=[], title='Rendite [%]')
   )
).configure_axisX(
    labelAngle=0,
    labelLimit=200,
    labelFontSize=12,
).properties(
    height=300
)
st.altair_chart(chart_irr)

###### Bewertung - Amortisationsdauer ######

st.markdown('Und wenn man Investition zu der Ersparnis an Betriebskosten ins Verhältnis setzt ergibt sich die Amortisationsdauer (ohne Abzinsung) wie folgt:')
chart_payback_data = pd.DataFrame({'Konzept': ['Ohne Solar','Volleinspeisung','Gemeinschaftliche Gebäudeversorgung','Mieterstrom'],
                                    'Rendite': payback})
chart_payback = (
   alt.Chart(chart_payback_data)
   .mark_bar()
   .encode(
       x=alt.X('Konzept:N', sort=[]),
       y=alt.Y('Rendite:Q', sort=[], title='Amortisationsdauer [Jahre]')
   )
).configure_axisX(
    labelAngle=0,
    labelLimit=200,
    labelFontSize=12,
).properties(
    height=300
)
st.altair_chart(chart_payback)

st.header('Wie setzt ihr es um?', anchor='umsetzung')

st.markdown('**Weitere Infos zur Beschlussfassung in der WEG und zur Umsetzung folgen...** :sunny:')

st.divider()

md_footer = '''
_Created with :heart:  in Köln-Zollstock using [Streamlit](https://streamlit.io/). Code: https://github.com/timorichert/weg-solar. Copyright 2025._
'''
st.markdown(md_footer)