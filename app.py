import streamlit as st
import pandas as pd
import numpy as np
import numpy_financial as npf

import functions as fn
import config as cfg

st.set_page_config(
    page_title="wegsolar.de | Solar für Wohnungseigentümergemeinschaften",
    page_icon="sunny"
)

###### HEADER ######
st.title(':sunny: Solar für _Wohnungs-eigentümergemeinschaften_')
st.markdown('Ihr seid eine WEG und wollt eine Solaranlage bauen, wisst aber nicht ob das für euch Sinn macht oder wie das geht? Dann seid ihr hier richtig! :smile: Hier könnt ihr zügig analysieren ob sich Photovoltaik für euch lohnt _(und später auch lernen wie ihr es dann umsetzt)_. Los geht''s... :sun_with_face: ')
st.warning('_:warning: :red[**ACHTUNG!** Dies ist aktuell nur ein Prototyp mit begrenzter Funktionsfähigkeit. Einiges funktioniert noch nicht (Schätzung Solar-Output als Funktion der Modulausrichtung, etc.). Einiges ist noch nicht abschließend sauber geprüft. Schreibt mir gerne Ideen und Feedback: '+ cfg.email +'.]_')

###### HAUS ######

st.header('Euer Haus', anchor='haus')
st.markdown('Macht hier Angaben zum Ist-Zustand eures Hauses.')

number_apartments = st.number_input('Anzahl der Wohnungen:', min_value=0, max_value=50, value=14, key='we')
power_consumption_per_apartment = st.number_input('Stromverbrauch pro Wohnung im Jahr [kWh] (im Schnitt könnt ihr im Mehrfamilienhaus von ca. 2500 kWh/Jahr pro Haushalt ausgehen. Singles natürlich weniger, Familien mehr.)', min_value=0, max_value=10000, value=2500, key='stromverbrauch')
number_meters = number_apartments + 1

power_price = st.number_input('Mittlerer Strompreis (inkl. Steuern) mit eurem Stromversorgungsvertrag [ct/kWh]:', min_value=20, max_value=40, value=32, key='power_price')
power_base_price = st.number_input('Mittlere monatliche Grundgebühr (inkl. Steuern) pro Wohnung für eure Stromversorgungsverträge [EUR/Monat]:', min_value=10, max_value=30, value=20, key='power_base_price')

power_consumption_total = number_apartments * power_consumption_per_apartment * 1.1 # [kWh]
cost_power_annual = power_consumption_total * power_price / 100 + 12 * number_meters * power_base_price

st.write('Ihr verbraucht in eurem Haus ca. __' + str(fn.zahlenformat(power_consumption_total, 0)) + ' kWh__ Strom pro Jahr (inklusive zusätzlich ca. 10% für den Allgemeinstrom). Dafür bezahlt ihr mit Grundgebühren und Arbeitspreis __ca. ' + str(fn.zahlenformat(cost_power_annual, 0)) + ' EUR__ im Jahr.')

st.header('Eure zukünftige Photovoltaik-Anlage', anchor='anlage')
st.markdown('''
Gebt hier an, wie eure zukünftige Anlage aussehen soll.
''')

# st.number_input('Postleitzahl (zur Abschätzung der Sonneneinstrahlung)', min_value=0, max_value=99999, key='plz')
capacity_kWp = st.number_input('Kapazität der Anlage [kWp] - Auf Google Maps könnt ihr eure freie Dachfläche abschätzen. Pro freiem Quadratmeter können ca. 0.2 kWp installiert werden.', min_value=0, max_value=200, value=21, key='capacity_kWp')
fn.warnung('Wie viel Kapazität ihr am Ende wirklich - mit Berücksichtigung von Verschattungen - sinnvoll auf dem Dach montieren könnt kann euch abschließend nur ein Fachbetrieb sagen. Hier könnt ihr aber mit einer Annahme starten.')

# st.number_input('Anstellwinkel der Anlage [Grad]', min_value=0, max_value=200, value=10, key='angle_deg', help='Bei Flachdächern wird die Anlage typischerweise mit einem Winkel von 10 bis 15 Grad installiert. Bei Spitzdächern entspricht der Winkel dem Dachwinkel.')
cost_specific = st.number_input('Spezifische Baukosten der Anlage [EUR/kWp] (typisch sind ca. 1200 bis 1400 EUR/kWp für eine Anlage ohne Speicher)', min_value=1000, max_value=1600, value=1400, key='specific_cost')
cost_inv_pv = cost_specific * capacity_kWp

pv_production = capacity_kWp * cfg.specific_production # [kWh]

einspeiseverguetung = [0, fn.calc_einspeiseverguetung("VE", capacity_kWp), fn.calc_einspeiseverguetung("UE", capacity_kWp), fn.calc_einspeiseverguetung("UE", capacity_kWp)] # [EUR/kWh]
# st.write(einspeiseverguetung)

self_consumption_fraction = round(fn.eigenverbrauch(capacity_kWp, power_consumption_total), 3)
power_consumption_self = pv_production * self_consumption_fraction
autarkiegrad = power_consumption_self / power_consumption_total

einspeisung_eigenverbrauch = pv_production - power_consumption_self
einspeisung_voll = pv_production

power_consumption_reststrom = power_consumption_total - power_consumption_self

st.write('Die Solaranlage kostet euch __' + str(fn.zahlenformat(cost_inv_pv, 0)) + ' EUR__ und  wird __ca. ' + str(fn.zahlenformat(pv_production, 0)) + ' kWh__ Strom pro Jahr produzieren.')
st.write('Bei eurem Jahresverbrauch werdet ihr davon ca. __' + str(fn.zahlenformat(self_consumption_fraction*100, 0)) + '% selbst verbrauchen__ ("Eigenverbrauchsquote"), also ca. ' + str(fn.zahlenformat(power_consumption_self, 0)) + ' kWh pro Jahr. __Damit deckt ihr euren jährlichen Gesamtbedarf zu ca. ' + str(fn.zahlenformat(autarkiegrad * 100, 0)) + '%__ ("Autkariegrad"). Den restlichen Solarstrom, also ' + str(fn.zahlenformat(einspeisung_eigenverbrauch, 0)) + ' kWh, speist ihr in das Stromnetz ein.')
st.write('(Die Errechnung des Eigenverbrauchs basiert auf den Methoden des [Solarrechners](https://solar.htw-berlin.de/rechner/) der [Hochschule für Technik und Wirtschaft Berlin](https://www.htw-berlin.de/))')

st.header('Nutzung des Solarstroms im Haus', anchor='nutzung')

mk = '''
Es gibt verschiedene Arten, den Strom im Haus zu nutzen. Die Nutzungsarten laufen unter dem Fachbegriff "Messkonzepte" und die drei interessantesten Ausprägungen sind:
- **Volleinspeisung** - Der Strom wird bilanziell komplett ins Stromnetz eingespeist und daher gibt es nur einen Einspeisezähler an der PV-Anlage. Für den eingespeisten Strom erhaltet ihr eine Einspeisevergütung. Ihr bezieht weiterhin den Strom für die Wohnungen von euren Stromversorgern.
- **Gemeinschaftliche Gebäudeversorgung** (GGV) - Jede Wohnung wird mit einem  ["intelligenten Messsystem" bzw. iMsys](https://www.bundesnetzagentur.de/DE/Vportal/Energie/Metering/start.html) ausgestattet (landläufig auch Smart Meter genannt). Hiermit kann euer Stromverbrauch in viertelstundengenauer Auflösung gemessen werden. Mit Hilfe eines Abrechnungsdienstleisters, der diese Solarstrommengen den teilnehmenden Haushalten zurechnet, kann der Solarstrom nun den Wohnungen zugeteilt werden. Gesetzlich geregelt wird die erst seit Mitte 2024 rechtskräftige GGV durch [EnWG §42b](https://www.gesetze-im-internet.de/enwg_2005/__42a.html).
- **Mieterstrom** - Bei diesem Konzept kann der Strom ebenfalls in den Wohnungen genutzt werden, und trotz des Begriffs "Mieterstrom" kann dieses Konzept auch für WEGs sehr sinnvoll sein. Im Gegensatz zur GGV, bei dem alle Solarstromnutzer ihre bisherigen Stromlieferverträge behalten, schließt nun ihr als WEG die Stromlieferverträge mit den Hausbewohnern ab. Auch für dieses Konzept braucht es die richtige Messtechnik. Traditionell wurde das Konzept häufig mit einem "physikalischen Summenzähler" umgesetzt, also mit einer aufwändigen Messung des Hausstromes am Hausanschluss. Mittlerweile etabliert sich aber mehr und mehr der ["virtuelle Summenzähler"](https://www.sfv.de/5-fragen-virtueller-summenzaehler), der wie auch die GGV auf iMsys basiert. Mieterstrom ist im [EnWG §42a](https://www.gesetze-im-internet.de/enwg_2005/__42a.html) reguliert.

Mehr Details zu diesen und weiteren Messkonzepten findet ihr auf dieser exzellenten :heart: Website der [Energieagentur Regio Freiburg](https://energieagentur-regio-freiburg.eu/): https://energieagentur-regio-freiburg.eu/pv-mehrparteienhaus/. Im Folgenden möchten wir uns aber noch nicht in Details verfangen, sondern die drei Konzept mal direkt vergleichen! :muscle:

'''

st.markdown(mk)
st.header('Kosten und Wirtschaftlichkeit', anchor='wirtschaftlichkeit')

st.subheader('Investitionskosten')
md_investment = '''Die Umsezung der einzelnen Konzepte ist mit den folgenden  Kosten verbunden:

- **Bau Solaranlage** - Dies umfasst Material und Installation der Solarmodule inklusive Befestigungsmitteln, Wechselrichter, Verkabelung, Anschluss an das Zählerfeld und Inbetriebnahme und Anmeldung der Anlage. Der Bau der Anlage wird als einzelner Auftrag an einen von euch gewählten Fachbetrieb vergeben.
- **Umsetzung Messkonzept** - Dies umfasst den Einbau bzw. den Umbau der Zähler. Das Messkonzept kann durch einen wettbewerblichen (wMSB) oder aber durch euren grundzuständigen (gMSB) Messstellenbetreiber umgesetzt werden. Der gMSB stellt für ein [vorzeitige](## "as") Umrüstung auf ein Smart Meter bis zu 100 EUR pro Zähler in Rechnung. Dies ist der maximal zulässige Betrag gemäß Solarspitzengesetz und hier unsere Annahme. In unserem Beispiel gehen von der Realisierung eines virtuellen Summenzählers über den gMSB aus, der den Zählertausch organisiert.
- **Einrichtungspauschale Abrechnungsdienstleister** - Der Dienstleister, der euch bei der korrekten Bilanzierung und Abrechnung des Solarstroms unterstützt, verlangt eine Einrichtungspauschale und unterstützt dafür auch bei der sauberen Umsetzung des Messkonzeptes und den dafür notwendigen Formalitäten. 
- **Beratungskosten** - Im Rahmen der Ausarbeitung des Gesamt-Konzeptes fallen gegebenenfalls noch Kosten für externe Beratung an. Dafür sehen wir hier auch einen kleinen Betrag vor.

'''

st.markdown(md_investment)
fn.warnung('In manchen und insbesondere in älteren Häusern sind noch weitere Umbauten notwendig, die ggf. zusätzliche Kosten verursachen. Dies solltet ihr von einem Elektroinstallationsbetrieb prüfen lassen.')

cat_inv_solaranlage = "Bau Solaranlage"
cost_inv_solaranlage = [0, cost_inv_pv, cost_inv_pv, cost_inv_pv]

cat_inv_abrechnung = "Einrichtungspauschale Abrechnungsdienstleister"
cost_inv_abrechnung = [0, 0, 2000, 2000]

cat_inv_messkonzept = "Umsetzung Messkonzept"
cost_inv_messkonzept = [0, 0, 100 * number_meters, 100 * number_meters]

cat_inv_beratung = "Beratung"
cost_inv_beratung = [0, 1000, 1000, 1000]

cost_inv_total = [0, 0, 0, 0]
for i in range (0, 4):
    cost_inv_total[i] = cost_inv_solaranlage[i] + cost_inv_abrechnung[i] + cost_inv_messkonzept[i] + cost_inv_beratung[i]

cost_inv_array = fn.one_dim_list(fn.transpose_list([cost_inv_solaranlage, cost_inv_abrechnung, cost_inv_messkonzept, cost_inv_beratung]))

chart_inv_data = pd.DataFrame({'Konzept': ['Ohne Solar', 'Ohne Solar', 'Ohne Solar', 'Ohne Solar',
                                                'Volleinspeisung','Volleinspeisung','Volleinspeisung','Volleinspeisung',
                                                'Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung',
                                                'Mieterstrom','Mieterstrom','Mieterstrom','Mieterstrom'],
                                    'Kategorie': ['Bau Solaranlage', 'Umsetzung Messkonzept', 'Einrichtungspauschale Abrechnungsdienstleister', 'Beratung',
                                                'Bau Solaranlage', 'Umsetzung Messkonzept', 'Einrichtungspauschale Abrechnungsdienstleister', 'Beratung',
                                                'Bau Solaranlage', 'Umsetzung Messkonzept', 'Einrichtungspauschale Abrechnungsdienstleister', 'Beratung',
                                                'Bau Solaranlage', 'Umsetzung Messkonzept', 'Einrichtungspauschale Abrechnungsdienstleister', 'Beratung'],
                                    'Kosten': cost_inv_array})

fn.create_chart(chart_inv_data, 'Kosten', 'Kategorie', 'Investitionskosten [EUR]', 500, True)

st.subheader('Betriebskosten und Einnahmen')
md_op = '''Im Betrieb lassen sich Ausgaben und Einnahmen der Anlage wie folgt beschreiben:

- **Grundgebühren Stromlieferverträge** - Beim Mieterstrom habt ihr als WEG einen einzigen gemeinsamen Stromliefervertrag und rechnet die Verbräuche innerhalb des Hauses ab. Bei allen anderen Konzepten behält jeder Bewohner seinen Stromliefervertrag.
- **Einkauf Netzstrom und Reststrom** - Durch die Nutzung des Solarstroms müsst ihr bei Mieterstrom oder GGV insgesamt natürlich weniger Strom einkaufen. Bei Volleinspeisung kauft ihr weiterhin sämtlichen Strom vom Stromversorger.
- **Betrieb Zähler für Wohnungen und Allgemeinstrom** - Bei Mieterstrom bezahlt ihr separat für den Betrieb der Zähler, während diese Gebühr bei Volleinspeisung und GGV in den monatlichen Grundgebühren eurer Stromlieferverträge bereits enthalten ist.
- **Betrieb Zähler Solaranlage** - Die Solaranlage hat einen Einspeisezähler, für den ebenfalls eine jährliche Gebühr zu entrichten ist.
- **Einnahmen aus der Einspeisevergütung** - Für den eingespeisten Solarstrom bekommt ihr eine Einspeisevergütung. Diese [errechnet sich aus der Anlagengröße](https://www.finanztip.de/photovoltaik/einspeiseverguetung/). Bei GGV und Mieterstrom gibt bei eurer Anlagengröße eine Einspeisevergütung von ''' + str(fn.zahlenformat(einspeiseverguetung[2] * 100, 2)) + ''' ct/kWh. Bei der Volleinspeisung gibt es einen Zuschlag und ihr bekommt so ''' + str(fn.zahlenformat(einspeiseverguetung[1] * 100, 2)) + ''' ct/kWh.
- **Einnahmen aus Mieterstromzuschlag** - Beim Mieterstrom erhaltet für jede im Haus verbrauchte Kilowattstunde Solarstrom einen Mieterstromzuschlag in Höhe von ca. ''' + str(fn.zahlenformat(cfg.mieterstromzuschlag[3] * 100, 2)) + ''' ct/kWh.

'''
st.markdown(md_op)

fn.warnung('In dieser Rechnung gehen wir aktuell davon aus, dass alle Hausbewohner bei GGV und Mieterstrom mitmachen, also eine Teilnehmerquote von 100%. Realistisch sind eher um die 80%. Dies werdet ihr hier zukünftig anpassen können. Schaut bald wieder vorbei!')
st.markdown('Im folgenden Diagramm sind eure voraussichtlichen jährlichen Ausgaben und - als negative Werte - Einnahmen dargestellt:')

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
cost_op_anlagenbetrieb = np.multiply(cost_inv_total, cfg.operating_cost_fraction).tolist()

cat_op_abrechnung = "Abrechnungsdienstleister"
cost_op_abrechnung = [0, 0, 5 * 12 * number_meters, 5 * 12 * number_meters]

cat_op_einnahmen_esv = "Einspeisevergütung"
einspeisung = [0, -einspeisung_voll, -einspeisung_eigenverbrauch, -einspeisung_eigenverbrauch]
cost_op_einnahmen_esv = np.multiply(einspeisung, einspeiseverguetung).tolist()

cat_op_einnahmen_msz = "Mieterstromzuschlag"
eigenverbrauch = [0, 0, -power_consumption_self, -power_consumption_self]
cost_op_einnahmen_msz = np.multiply(eigenverbrauch, cfg.mieterstromzuschlag).tolist()

cost_op_total = [0, 0, 0, 0]
for i in range (0, 4):
    cost_op_total[i] = cost_op_meters[i] + cost_op_solarmeter[i] + cost_op_grundgebuehr[i] + cost_op_reststrom[i] + cost_op_anlagenbetrieb[i] + cost_op_abrechnung[i] + cost_op_einnahmen_esv[i] + cost_op_einnahmen_msz[i]

cost_op_array = fn.one_dim_list(fn.transpose_list([cost_op_meters, cost_op_solarmeter, cost_op_grundgebuehr, cost_op_reststrom, cost_op_anlagenbetrieb, cost_op_abrechnung, cost_op_einnahmen_esv, cost_op_einnahmen_msz]))
chart_op_data = pd.DataFrame({'Konzept': ['Ohne Solar', 'Ohne Solar', 'Ohne Solar', 'Ohne Solar', 'Ohne Solar', 'Ohne Solar', 'Ohne Solar', 'Ohne Solar',
                                                'Volleinspeisung','Volleinspeisung','Volleinspeisung','Volleinspeisung','Volleinspeisung','Volleinspeisung','Volleinspeisung','Volleinspeisung',
                                                'Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung','Gemeinschaftliche Gebäudeversorgung',
                                                'Mieterstrom','Mieterstrom','Mieterstrom','Mieterstrom','Mieterstrom','Mieterstrom','Mieterstrom','Mieterstrom'],
                                    'Kategorie': [cat_op_meters, cat_op_solarmeter, cat_op_grundgebuehr, cat_reststrom, cat_op_anlagenbetrieb, cat_op_abrechnung, cat_op_einnahmen_esv, cat_op_einnahmen_msz,
                                                  cat_op_meters, cat_op_solarmeter, cat_op_grundgebuehr, cat_reststrom, cat_op_anlagenbetrieb, cat_op_abrechnung, cat_op_einnahmen_esv, cat_op_einnahmen_msz,
                                                  cat_op_meters, cat_op_solarmeter, cat_op_grundgebuehr, cat_reststrom, cat_op_anlagenbetrieb, cat_op_abrechnung, cat_op_einnahmen_esv, cat_op_einnahmen_msz,
                                                  cat_op_meters, cat_op_solarmeter, cat_op_grundgebuehr, cat_reststrom, cat_op_anlagenbetrieb, cat_op_abrechnung, cat_op_einnahmen_esv, cat_op_einnahmen_msz],
                                    'Kosten': cost_op_array})

fn.create_chart(chart_op_data, 'Kosten', 'Kategorie', 'Betriebskosten [EUR/Jahr]', 500, True)

st.subheader('Wirtschaftlichkeit')
st.markdown('Aus den Investitionskosten und den durch die Solaranlage reduzierten Betriebskosten sowie den zusätzlichen Einnahmen lassen sich nun wirtschaftliche Kenngrößen herleiten.')

###### Calculate Economics ######

payback = [0, 0, 0, 0]
irr_percent = [0, 0, 0, 0]
for i in range (1, 4):
    rel_investment_cost = cost_inv_total[i] - cost_inv_total[0]
    rel_operating_cost = cost_op_total[i] - cost_op_total[0]
    payback[i] = round(- rel_investment_cost / rel_operating_cost, 1)

    cashflow = [0] * 22
    cashflow[0] = -rel_investment_cost
    for a in range (1, 21 + 1):
        cashflow[a] = -rel_operating_cost

    irr_percent[i] = round(npf.irr(cashflow) * 100, 1)

###### Bewertung - Rendite ######
st.markdown('Die __Rendite der Investition__ - gerechnet über 20 Jahre - sieht wie folgt aus:')
chart_irr_data = pd.DataFrame({'Konzept': ['Ohne Solar','Volleinspeisung','Gemeinschaftliche Gebäudeversorgung','Mieterstrom'],
                                    'Rendite': irr_percent})
fn.create_chart(chart_irr_data, 'Rendite', 'Konzept', 'Rendite [%]', 360, False)

###### Bewertung - Amortisationsdauer ######
st.markdown('Und wenn man Investition zu der Ersparnis an Betriebskosten und Einnahmen ins Verhältnis setzt ergibt sich die __Amortisationsdauer__ (ohne Abzinsung) wie folgt:')
chart_payback_data = pd.DataFrame({'Konzept': ['Ohne Solar','Volleinspeisung','Gemeinschaftliche Gebäudeversorgung','Mieterstrom'],
                                    'Amortisationsdauer': payback})
fn.create_chart(chart_payback_data, 'Amortisationsdauer', 'Konzept', 'Amortisationsdauer [Jahre]', 360, False)



###### Umsetzung ######

st.header('Wie setzt ihr es um?', anchor='umsetzung')

st.markdown('**Weitere Infos zur Beschlussfassung in der WEG und zur Umsetzung folgen...** :sunny:')

st.divider()

md_footer = '''
_Created with :heart:  in Köln-Zollstock using [Streamlit](https://streamlit.io/). App hosted at [Heroku](https://www.heroku.com/). The code is available at [Github/timorichert/weg-solar](https://github.com/timorichert/weg-solar). Copyright 2025._
'''
st.markdown(md_footer)