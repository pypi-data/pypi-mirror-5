# Copyright (C) 2013 Brian Wesley Baugh
"""Tools for estimating country location data."""
import math

# Average latitude and longitude for countries.
# Data from <http://dev.maxmind.com/geoip/codes/country_latlon>.
# The site claims the source is from the CIA World Factbook.
# Some edits have been made in reference to:
#    <https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2#Decoding_table>
# Format: "iso 3166 country","latitude","longitude"
COUNTRIES = (
    """
AD,42.5000,1.5000
AE,24.0000,54.0000
AF,33.0000,65.0000
AG,17.0500,-61.8000
AI,18.2500,-63.1667
AL,41.0000,20.0000
AM,40.0000,45.0000
"""  # AN,12.2500,-68.7500 (deleted from ISO 3166-1 but reserved transitionally)
    """AO,-12.5000,18.5000
"""  # AP,35.0000,105.0000 (not used; international property organisation names)
    """AQ,-90.0000,0.0000
AR,-34.0000,-64.0000
AS,-14.3333,-170.0000
AT,47.3333,13.3333
AU,-27.0000,133.0000
AW,12.5000,-69.9667
AZ,40.5000,47.5000
BA,44.0000,18.0000
BB,13.1667,-59.5333
BD,24.0000,90.0000
BE,50.8333,4.0000
BF,13.0000,-2.0000
BG,43.0000,25.0000
BH,26.0000,50.5500
BI,-3.5000,30.0000
BJ,9.5000,2.2500
BM,32.3333,-64.7500
BN,4.5000,114.6667
BO,-17.0000,-65.0000
BR,-10.0000,-55.0000
BS,24.2500,-76.0000
BT,27.5000,90.5000
BV,-54.4333,3.4000
BW,-22.0000,24.0000
BY,53.0000,28.0000
BZ,17.2500,-88.7500
CA,60.0000,-95.0000
CC,-12.5000,96.8333
CD,0.0000,25.0000
CF,7.0000,21.0000
CG,-1.0000,15.0000
CH,47.0000,8.0000
CI,8.0000,-5.0000
CK,-21.2333,-159.7667
CL,-30.0000,-71.0000
CM,6.0000,12.0000
CN,35.0000,105.0000
CO,4.0000,-72.0000
CR,10.0000,-84.0000
CU,21.5000,-80.0000
CV,16.0000,-24.0000
CX,-10.5000,105.6667
CY,35.0000,33.0000
CZ,49.7500,15.5000
DE,51.0000,9.0000
DJ,11.5000,43.0000
DK,56.0000,10.0000
DM,15.4167,-61.3333
DO,19.0000,-70.6667
DZ,28.0000,3.0000
EC,-2.0000,-77.5000
EE,59.0000,26.0000
EG,27.0000,30.0000
EH,24.5000,-13.0000
ER,15.0000,39.0000
ES,40.0000,-4.0000
ET,8.0000,38.0000
"""  # EU,47.0000,8.0000 (reserved on request for restricted use.)
    """FI,64.0000,26.0000
FJ,-18.0000,175.0000
FK,-51.7500,-59.0000
FM,6.9167,158.2500
FO,62.0000,-7.0000
FR,46.0000,2.0000
GA,-1.0000,11.7500
GB,54.0000,-2.0000
GD,12.1167,-61.6667
GE,42.0000,43.5000
GF,4.0000,-53.0000
GH,8.0000,-2.0000
GI,36.1833,-5.3667
GL,72.0000,-40.0000
GM,13.4667,-16.5667
GN,11.0000,-10.0000
GP,16.2500,-61.5833
GQ,2.0000,10.0000
GR,39.0000,22.0000
GS,-54.5000,-37.0000
GT,15.5000,-90.2500
GU,13.4667,144.7833
GW,12.0000,-15.0000
GY,5.0000,-59.0000
HK,22.2500,114.1667
HM,-53.1000,72.5167
HN,15.0000,-86.5000
HR,45.1667,15.5000
HT,19.0000,-72.4167
HU,47.0000,20.0000
ID,-5.0000,120.0000
IE,53.0000,-8.0000
IL,31.5000,34.7500
IN,20.0000,77.0000
IO,-6.0000,71.5000
IQ,33.0000,44.0000
IR,32.0000,53.0000
IS,65.0000,-18.0000
IT,42.8333,12.8333
JM,18.2500,-77.5000
JO,31.0000,36.0000
JP,36.0000,138.0000
KE,1.0000,38.0000
KG,41.0000,75.0000
KH,13.0000,105.0000
KI,1.4167,173.0000
KM,-12.1667,44.2500
KN,17.3333,-62.7500
KP,40.0000,127.0000
KR,37.0000,127.5000
KW,29.3375,47.6581
KY,19.5000,-80.5000
KZ,48.0000,68.0000
LA,18.0000,105.0000
LB,33.8333,35.8333
LC,13.8833,-61.1333
LI,47.1667,9.5333
LK,7.0000,81.0000
LR,6.5000,-9.5000
LS,-29.5000,28.5000
LT,56.0000,24.0000
LU,49.7500,6.1667
LV,57.0000,25.0000
LY,25.0000,17.0000
MA,32.0000,-5.0000
MC,43.7333,7.4000
MD,47.0000,29.0000
ME,42.0000,19.0000
MG,-20.0000,47.0000
MH,9.0000,168.0000
MK,41.8333,22.0000
ML,17.0000,-4.0000
MM,22.0000,98.0000
MN,46.0000,105.0000
MO,22.1667,113.5500
MP,15.2000,145.7500
MQ,14.6667,-61.0000
MR,20.0000,-12.0000
MS,16.7500,-62.2000
MT,35.8333,14.5833
MU,-20.2833,57.5500
MV,3.2500,73.0000
MW,-13.5000,34.0000
MX,23.0000,-102.0000
MY,2.5000,112.5000
MZ,-18.2500,35.0000
NA,-22.0000,17.0000
NC,-21.5000,165.5000
NE,16.0000,8.0000
NF,-29.0333,167.9500
NG,10.0000,8.0000
NI,13.0000,-85.0000
NL,52.5000,5.7500
NO,62.0000,10.0000
NP,28.0000,84.0000
NR,-0.5333,166.9167
NU,-19.0333,-169.8667
NZ,-41.0000,174.0000
OM,21.0000,57.0000
PA,9.0000,-80.0000
PE,-10.0000,-76.0000
PF,-15.0000,-140.0000
PG,-6.0000,147.0000
PH,13.0000,122.0000
PK,30.0000,70.0000
PL,52.0000,20.0000
PM,46.8333,-56.3333
PR,18.2500,-66.5000
PS,32.0000,35.2500
PT,39.5000,-8.0000
PW,7.5000,134.5000
PY,-23.0000,-58.0000
QA,25.5000,51.2500
RE,-21.1000,55.6000
RO,46.0000,25.0000
RS,44.0000,21.0000
RU,60.0000,100.0000
RW,-2.0000,30.0000
SA,25.0000,45.0000
SB,-8.0000,159.0000
SC,-4.5833,55.6667
SD,15.0000,30.0000
SE,62.0000,15.0000
SG,1.3667,103.8000
SH,-15.9333,-5.7000
SI,46.0000,15.0000
SJ,78.0000,20.0000
SK,48.6667,19.5000
SL,8.5000,-11.5000
SM,43.7667,12.4167
SN,14.0000,-14.0000
SO,10.0000,49.0000
SR,4.0000,-56.0000
ST,1.0000,7.0000
SV,13.8333,-88.9167
SY,35.0000,38.0000
SZ,-26.5000,31.5000
TC,21.7500,-71.5833
TD,15.0000,19.0000
TF,-43.0000,67.0000
TG,8.0000,1.1667
TH,15.0000,100.0000
TJ,39.0000,71.0000
TK,-9.0000,-172.0000
TM,40.0000,60.0000
TN,34.0000,9.0000
TO,-20.0000,-175.0000
TR,39.0000,35.0000
TT,11.0000,-61.0000
TV,-8.0000,178.0000
TW,23.5000,121.0000
TZ,-6.0000,35.0000
UA,49.0000,32.0000
UG,1.0000,32.0000
UM,19.2833,166.6000
US,38.0000,-97.0000
UY,-33.0000,-56.0000
UZ,41.0000,64.0000
VA,41.9000,12.4500
VC,13.2500,-61.2000
VE,8.0000,-66.0000
VG,18.5000,-64.5000
VI,18.3333,-64.8333
VN,16.0000,106.0000
VU,-16.0000,167.0000
WF,-13.3000,-176.2000
WS,-13.5833,-172.3333
YE,15.0000,48.0000
YT,-12.8333,45.1667
ZA,-29.0000,24.0000
ZM,-15.0000,30.0000
ZW,-20.0000,30.0000
""").strip().split('\n')
COUNTRIES = [x.split(',') for x in COUNTRIES]


def estimated_country(latitude, longitude):
    """Estimate what country belongs to a latitude and longitude point.

    Args:
        latitude: Float of the (normalized) latitude coordinate of the
            point.
        longitude: Float of the (normalized) longitude coordinate of the
            point.

    Returns:
        Uppercase string of the two letter ISO-3166 country code of the
        estimated country.
    """
    best_country, best_distance = None, None
    for country, lat_coord, lon_coord in COUNTRIES:
        # Euclidean distance.
        distance = math.sqrt((latitude - float(lat_coord)) ** 2 +
                             (longitude - float(lon_coord)) ** 2)
        distance = -distance  # Values near zero are less distant.
        if distance > best_distance:
            best_country, best_distance = country, distance
    return best_country
