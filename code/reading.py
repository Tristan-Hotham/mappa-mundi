"""Hand decisions, made by reading Bevan and Phillott (1873) and the map itself.

LOCATED: the book's identification for every inscription I located by eye on Konrad Miller's 1896 facsimile
(data/map_positions.csv), keyed by (index name, page). Values: (identification, book page evidence, latitude, longitude).
  * identification: what the book says the name stands for, in its own words where possible ('Cochin', 'the city of
    Cairo'); None where the book gives no real place (legendary, or it says the name is unknown).
  * latitude, longitude: the position of that place today, which I supply for plotting; checked against Natural Earth
    and Pleiades in 02_geo.py (any disagreement over 30 km is reported and the gazetteer point is used).

Classes (the book's own four kinds of material, Introduction section 11: Biblical, classical, legendary and
contemporary, i.e. medieval), applied to all 1,025 names in its index by this rule, in order:
  1. Frame and natural history (left out of the shares): the winds, quarters and continent labels of the frame, and
     real animals and plants (FRAME_NAT).
  2. Legendary: monstrous peoples, fabulous beasts and the places and objects of legend and myth (LEGEND).
  3. Biblical: everything in the book's sections on the rivers of Paradise (p. 25 to 26), Palestine and Arabia (pp. 77
     to 81) and the Exodus in Egypt (pp. 84 to 86), and elsewhere names the Bible gives (BIBLE), less the Greek and Roman
     names listed in NOT_BIBLE.
  4. Medieval: in Europe and the British Isles, names that do not match a Greek or Roman name in the Pleiades
     gazetteer (a post-classical place or a post-classical name for it); in Asia and Africa only the few the book
     traces to medieval knowledge (MEDIEVAL_X).
  5. Classical: everything else (Greek and Roman names, mostly from Pliny, Solinus, Orosius, Isidore and the Antonine
     Itinerary).
"""

FRAME_NAT = {  # index keys
    391, 617, 685, 695, 859, 56, 63, 113, 164, 197, 276, 901, 956, 1000, 20, 21, 114, 392, 405, 563, 1021,   # winds and quarters
    96, 19, 390, 533,                                                    # continent labels; Layburnia (the author's prebend, p. 14)
    891, 521, 796, 204, 737, 561, 288, 536, 541, 853, 978, 868, 939, 594, 888}   # animals and plants; Sol (the sun, p. 83)

LEGEND = {720, 73, 131, 584, 462, 982, 630, 520, 226, 906, 172, 418, 477, 633, 263, 191, 446, 852, 198, 436, 274, 467,
          458, 761, 640, 639, 595, 348, 118, 752, 890, 404, 839, 599, 58, 466, 227, 485, 847, 156, 38, 52, 381, 496,
          23, 597, 434, 435, 750, 892, 938, 975, 134, 815, 155, 87, 122}
# Paradise, the dry and balsam trees, Magog, Gog, the Golden Fleece, the Minotaurs, the Labyrinth, Charybdis, Scylla,
# St Brandan and the Fortunate Isles, the Hesperides, the Wonderful Isle, the city of Magog, the sons of Cain, the mouth
# of hell, the ship rock, Calypso's isle, Ganzmir, the Gryphae, the giants, pygmies, one-eyed and dog-headed races,
# the unicorn, manticore, dragons, alerion, phoenix, sphinx, fauns, satyrs, the marsok, apterophon, griffins, Arimaspi,
# Himantopodes, Sciapodes, Blemmyes, Ambari, man-eaters, Essedones, Hyperboreans, Agriophagi, four-eyed Ethiopians,
# the Gangines, Phanesii, Spopodes, Tigolopes and Ugolopes, the basilisk, the salamander, Bizo, and the isles of
# Rams and Birds from the St Brandan story (p. 172).

BIBLE_PAGES = [(25, 26), (77, 81), (85, 86)]
BIBLE = {373, 857, 692, 74, 123, 124, 195, 493, 669, 0, 401, 931, 7, 76, 884, 547, 910}
# Enos, Sephar, Ophir, Noah's Ark, Babel, Babylon, Chaldea, Ur, Nineveh, Abana, Pharpar, Teman, Ekron, the Arkites,
# Zobah, Lebanon and Tahpanhes. New Testament towns outside the Holy Land (Ephesus, Tarsus, Antioch) stay classical.
NOT_BIBLE = {67, 243, 795, 749, 587, 1024, 638, 51, 125, 929, 618, 99, 100, 3, 778, 366}
# Arabia Deserta, Mount Cassius, Rhinocolura, Petra, Egyptian Babylon, the Thebaid, Meroe, the Nile rivers, Abydos,
# Ptolemais and Egypt itself: Greek and Roman names. Mahum, Zosimas and the monasteries are medieval (below).

MEDIEVAL_X = {826, 968, 587, 1024, 638, 51}   # Samarkand, the Turks, Mahun, St Zosimas, the monasteries of St Antony

LOCATED = {
    ("Paradisi porte", 25): (None, "Terrestrial Paradise, an island surrounded by a wall with flames (p. 25)", None, None),
    ("Arbor Sicca", 25): (None, "the dry tree (p. 25 to 27)", None, None),
    ("Gigantes", 27): (None, "the giants (Gen. vi. 4)", None, None),
    ("Enos", 27): (None, "Enos civitas antiquissima (Gen. iv. 17)", None, None),
    ("Cottonare", 27): ("Kochi (Cochin)", "Cottonara of Pliny and Solinus, now probably Cochin (p. 27)", 9.97, 76.27),
    ("Patalus", 28): ("the Indus delta (Patale)", "clearly Patale of Pliny, the district between Cutch and Kurrachee (p. 28)", 24.75, 67.9),
    ("Pigmei", 28): (None, "the pygmies (p. 28)", None, None),
    ("Nicea", 28): ("Nicaea on the Hydaspes (Jhelum)", "two towns founded by Alexander near the river Hydaspes (p. 28)", 32.95, 73.65),
    ("Bucephala", 28): ("Bucephala on the Hydaspes (Jhelum)", "two towns founded by Alexander near the river Hydaspes (p. 28)", 32.93, 73.73),
    ("Aree Alexandri", 28): (None, "the twelve altars set up by Alexander (p. 28); no site given", None, None),
    ("Avalerion", 30): (None, "the alerion, of which there is only one pair in the world (p. 30)", None, None),
    ("Cassica", 30): ("Capissa (Kapisa)", "no doubt Capissa, which Pliny says was destroyed by Cyrus (p. 30)", 35.0, 69.25),
    ("Polibrota", 32): ("Patna (Palimbothra)", "Palimbothra ... answers to the city of Patna (p. 32)", 25.61, 85.14),
    ("Zimarim", 33): ("Muziris, now probably Mangalore", "Zimaris ... Muziris, a commercial port ... now probably Mangalore (p. 33)", 12.87, 74.84),
    ("Tapbana", 34): ("Sri Lanka (Taprobane, Ceylon)", "the isle of Taprobane (Ceylon) (p. 21); a large triangular island, intended for Ceylon (p. 33)", 7.87, 80.77),
    ("Alexandria", 36): ("Alexandria in the Caucasus (Bagram)", "Alexandria, founded by Alexander, in the country of the Cadrusi (p. 36)", 35.0, 69.27),
    ("Samarcan", 52): ("Samarkand", "Samarkand, the Maracanda of Arrian and Ptolemy (p. 52)", 39.65, 66.96),
    ("Caspia", 52): (None, "Caspia civitas: not identified by the book", None, None),
    ("Magog", 49): (None, "the land of Gog and Magog (p. 49)", None, None),
    ("Carimaspi", 61): (None, "the Arimaspi fighting griffins for emeralds (p. 61)", None, None),
    ("Griphe", 61): (None, "the griffins (p. 61)", None, None),
    ("Caspie Portee", 64): ("the Caspian Gates", "the Caspian Gates, entered by a road eight miles long (p. 64)", 35.47, 52.6),
    ("Persepolis", 72): ("Persepolis", "Persepolis caput Persidis (p. 72)", 29.93, 52.89),
    ("Rages", 71): ("Rhagae (Rey, Tehran)", "Rages (Tobit; Rhagae) (p. 71)", 35.59, 51.44),
    ("Carax", 72): ("Charax Spasinou", "Pliny's description, Charax oppidum Persici sinus intimum (p. 72)", 30.94, 47.66),
    ("Ninevee", 73): ("Nineveh (Mosul)", "civitas Ninive (p. 73)", 36.36, 43.15),
    ("Samosaka", 73): ("Samosata", "Samosata, which was not in Mesopotamia, though on the Euphrates (p. 73)", 37.52, 38.48),
    ("Nisibi", 74): ("Nisibis (Nusaybin)", "Nisibis, placed incorrectly on the Euphrates (p. 74)", 37.07, 41.22),
    ("Babel Tttkris", 74): ("Babylon (the Tower of Babel)", "a tower, the Tower of Babel (Gen. xi. 5, 9) (p. 74)", 32.54, 44.42),
    ("Babylonia", 74): ("Babylon", "Babilonia a Nembroth gigante fundata (p. 74)", 32.54, 44.42),
    ("Hur", 74): ("Ur of the Chaldees", "Hur, Abraham's country in Chaldea (p. 74)", 30.96, 46.1),
    ("Area Noe", 69): ("the mountains of Armenia (Ararat)", "Archa Noe sedit in montibus Armenie (p. 69)", 39.7, 44.3),
    ("Tarsus", 68): ("Tarsus", "the city of Tarsus (p. 68)", 36.92, 34.9),
    ("Ephesus", 68): ("Ephesus", "Ephesus, on a nameless river, perhaps the Cayster (p. 68)", 37.94, 27.34),
    ("Antiochia", 68): ("Antioch in Pisidia", "probably Antioch in Pisidia (p. 68)", 38.31, 31.19),
    ("Troja", 69): ("Troy", "Troja (p. 69)", 39.96, 26.24),
    ("Nicomedia", 69): ("Nicomedia (Izmit)", "Nicomedia, in Bithynia (p. 69)", 40.77, 29.92),
    ("Calcidonia", 69): ("Chalcedon (Kadikoy)", "Calcidonia (Chalcedon), in Bithynia (p. 69)", 40.99, 29.03),
    ("Antiochia", 76): ("Antioch of Syria (Antakya)", "Antioch of Syria (p. 76)", 36.2, 36.16),
    ("Laodiciam", 76): ("Latakia (Laodicea of Syria)", "Laodicea of Syria, on the sea coast (p. 76)", 35.52, 35.78),
    ("Tripolis", 76): ("Tripoli, Lebanon", "Tripolis (p. 76)", 34.44, 35.85),
    ("Beritus", 76): ("Beirut", "Beritus (p. 76)", 33.89, 35.5),
    ("Damascus", 77): ("Damascus", "Damascus (p. 77)", 33.51, 36.29),
    ("Sodom", 77): ("Sodom, by the Dead Sea", "Sodoma and Gomorra on the surface of the Dead Sea (p. 77)", 31.05, 35.4),
    ("Loth uxor", 77): (None, "Lot's wife turned to a pillar of salt (Gen. xix. 26) (p. 77)", None, None),
    ("Petra", 77): ("Petra", "the city of Petra (p. 77)", 30.33, 35.44),
    ("Nazaret", 78): ("Nazareth", "Nazaret (p. 78)", 32.7, 35.3),
    ("Cesarea Philippi", 78): ("Caesarea Philippi (Banias)", "Cesarea Philippi (p. 78)", 33.25, 35.69),
    ("Tholomaida", 78): ("Acre (Ptolemais)", "Ptolemais (p. 78)", 32.92, 35.07),
    ("Carmelum", 78): ("Mount Carmel", "mons Carmelus (p. 78)", 32.73, 35.05),
    ("Jerusalem", 79): ("Jerusalem", "the city of Jerusalem, placed as the centre of the world (p. 79)", 31.78, 35.23),
    ("Bethleem", 79): ("Bethlehem", "Bethleem (p. 79)", 31.7, 35.2),
    ("Gaza", 79): ("Gaza", "Cuja, Gaza ... (p. 79)", 31.5, 34.47),
    ("Gerara", 79): ("Gerar", "probably Gerar (Gen. xx. 1) (p. 79)", 31.38, 34.6),
    ("Ascalon", 78): ("Ashkelon", "Ascalon (p. 78)", 31.67, 34.57),
    ("Bersabee", 80): ("Beersheba", "Bersabee (p. 80)", 31.25, 34.79),
    ("Ebron", 80): ("Hebron", "Hebron (p. 80)", 31.53, 35.1),
    ("Jerico", 80): ("Jericho", "Jerico (p. 80)", 31.86, 35.46),
    ("Sinay", 81): ("Mount Sinai", "mons Sinay, and near it Moyses (p. 81)", 28.54, 33.97),
    ("Phenix", 85): (None, "the phoenix (p. 85)", None, None),
    ("Babylonia", 86): ("Cairo", "Babilonia, the city of Cairo (p. 86)", 30.01, 31.23),
    ("Orrea Josepbi", 86): ("the Pyramids of Giza", "the granaries of Joseph, as the Pyramids used to be called in the Middle Ages (p. 86)", 29.98, 31.13),
    ("Mandragora", 87): (None, "the mandrake (p. 87)", None, None),
    ("Alexandria", 88): ("Alexandria", "Alexandria, with a figure of the Pharos (p. 88)", 31.2, 29.92),
    ("Siene", 84): ("Aswan (Syene)", "the tower and celebrated well of Syene (p. 84)", 24.09, 32.9),
    ("Berenice", 84): ("Berenice on the Red Sea", "Berenice, the well-known port on the Red Sea (p. 84)", 23.91, 35.47),
    ("Cirene", 92): ("Cyrene (Shahhat)", "Cirene (p. 92)", 32.82, 21.86),
    ("Berenice", 92): ("Benghazi (Berenice)", "Berenice, one of the towns of the Pentapolis (p. 92)", 32.12, 20.07),
    ("Aree Philenoram", 92): ("the Altars of the Philaeni", "Arae Philaenorum (p. 92)", 30.3, 18.98),
    ("Apollonia", 92): ("Apollonia (Susa, Libya)", "Apollonia, of the Pentapolis (p. 92)", 32.9, 21.97),
    ("Ptholomaida", 92): ("Ptolemais (Tolmeita)", "Ptolemais, of the Pentapolis (p. 92)", 32.71, 20.95),
    ("Arsinoe", 92): ("Arsinoe (Tocra, Teuchira)", "Teuchira, which is used by Isidore in lieu of Arsinoe (p. 92)", 32.53, 20.58),
    ("Leptis Magna", 93): ("Leptis Magna", "Leptis Magna (p. 93)", 32.64, 14.29),
    ("Sabrata", 93): ("Sabratha", "Sabrata (p. 93)", 32.8, 12.48),
    ("Cartago", 95): ("Carthage", "Cartago Magna, pictorially represented by an edifice of imposing dimensions (p. 95)", 36.86, 10.33),
    ("Suffetula", 96): ("Sufetula (Sbeitla)", "a central station in the interior, frequently mentioned in the Itinerary (p. 96)", 35.24, 9.12),
    ("Ippone", 97): ("Hippo Regius (Annaba)", "Hippone, the one always used in the Itinerary; Augustine's see (p. 97)", 36.88, 7.75),
    ("Cesarea", 99): ("Caesarea in Mauretania (Cherchell)", "Cesarea (p. 99)", 36.61, 2.19),
    ("Septem Montes", 99): ("Ceuta", "the station Ad septem Fratres ... at or near Ceuta (p. 99)", 35.89, -5.32),
    ("Scinopodes", 102): (None, "the Sciapodes (p. 102)", None, None),
    ("Blemee", 103): (None, "the Blemyae (p. 103)", None, None),
    ("Fortunate", 106): (None, "Fortunate Insule: sex sunt: insule Sancti Brandani (p. 106)", None, None),
    ("Gades", 112): ("Cadiz", "the town of Cadiz (p. 112)", 36.53, -6.29),
    ("Calpel", 99): ("Gibraltar (Calpe)", "Calpe or Gibraltar (p. 99)", 36.14, -5.35),
    ("Laborintus", 116): (None, "the Labyrinth of Daedalus (p. 116)", None, None),
    ("Caribdis", 116): (None, "Charybdis, the whirlpool (p. 116)", None, None),
    ("Messana", 116): ("Messina", "Messana (p. 116)", 38.19, 15.55),
    ("Venicia", 118): ("Venice", "Venice, the insular character of which is indicated with considerable exaggeration (p. 118)", 45.44, 12.33),
    ("Constantinopolis", 136): ("Istanbul (Constantinople)", "Constantinopolis (p. 136)", 41.01, 28.98),
    ("Thessalonica", 135): ("Thessaloniki", "Thessalonica (p. 135)", 40.64, 22.94),
    ("Athene", 134): ("Athens", "Athene (p. 134)", 37.98, 23.73),
    ("Roma", 130): ("Rome", "Roma caput mundi (p. 130)", 41.9, 12.49),
    ("Neapolis", 131): ("Naples", "Naples (p. 131)", 40.85, 14.27),
    ("Salema", 131): ("Salerno", "the ancient Salernum, a place of great fame in the Middle Ages for its school of medicine (p. 131)", 40.68, 14.77),
    ("Puteolis", 131): ("Pozzuoli", "Pozzuoli (p. 131)", 40.82, 14.12),
    ("Bononia", 130): ("Bologna", "Bononia (p. 130)", 44.49, 11.34),
    ("Arimmuin", 130): ("Rimini", "Ariminum (Rimini), which should have been placed on the sea coast (p. 130)", 44.06, 12.57),
    ("Vercellis", 130): ("Vercelli", "properly Vercellae (p. 130)", 45.32, 8.42),
    ("Genua", 131): ("Genoa", "Genoa (p. 131)", 44.41, 8.93),
    ("Arelas", 148): ("Arles", "Arelas (p. 148)", 43.68, 4.63),
    ("Narbona", 143): ("Narbonne", "Narbona (p. 143)", 43.18, 3.0),
    ("Tolosa", 147): ("Toulouse", "Toulouse (p. 147)", 43.6, 1.44),
    ("Burdegala", 147): ("Bordeaux", "Bordeaux, represented in a style proportioned to its importance (p. 147)", 44.84, -0.58),
    ("Bayona", 148): ("Bayonne", "Bayonne (p. 148)", 43.49, -1.47),
    ("Compostella", 125): ("Santiago de Compostela", "Compostella ... a place of pilgrimage (p. 125)", 42.88, -8.54),
    ("Iacobi Templum", 125): ("Santiago de Compostela (the shrine of St James)", "the temple of St James, one of the most frequented places of pilgrimage (p. 125)", 42.88, -8.54),
    ("Toletum", 126): ("Toledo", "Toletum (p. 126)", 39.86, -4.03),
    ("Corduba", 126): ("Cordoba", "Cordova, which succeeded Carthagena as a metropolitan see (p. 126)", 37.88, -4.78),
    ("Basella", 126): ("Seville", "probably intended for Seville (p. 126)", 37.39, -5.98),
    ("Terracona", 126): ("Tarragona", "Terracona (p. 126)", 41.12, 1.25),
    ("Ilema", 126): ("Lleida (Lerida)", "may possibly be Ilerda, Lerida (p. 126)", 41.62, 0.62),
    ("Parisius", 145): ("Paris", "Paris (p. 145)", 48.86, 2.35),
    ("Remis", 145): ("Reims", "Rheims, the ancient Remi or Durocortorum, an archiepiscopal see (p. 145)", 49.26, 4.03),
    ("Rotomagum", 145): ("Rouen", "Rouen, the metropolis of Normandy, as Higden styles it (p. 145)", 49.44, 1.1),
    ("Carnotum", 146): ("Chartres", "Carnutum, Chartres (p. 146)", 48.45, 1.49),
    ("Cenomani", 146): ("Le Mans", "Cenomani, Le Mans (p. 146)", 48.0, 0.2),
    ("Aurelianum", 146): ("Orleans", "on the Loire, Aurelianum, Orleans (p. 146)", 47.9, 1.9),
    ("Turonis", 147): ("Tours", "Turonis (p. 147)", 47.39, 0.69),
    ("Limogena", 147): ("Limoges", "either Limoges ... or else Limagne (p. 147)", 45.83, 1.26),
    ("Avernis", 147): ("Clermont-Ferrand", "probably Clermont, which was known as Arverna (p. 147)", 45.78, 3.08),
    ("Augustudunum", 145): ("Autun", "Augustodunum, Autun (p. 145)", 46.95, 4.3),
    ("Remesburgh", 154): ("Regensburg", "Ratisbon, under its German designation Regensburg (p. 154)", 49.02, 12.1),
    ("Braga", 152): ("Prague", "Braga metropolis Boemariorum, Prague (p. 151)", 50.08, 14.42),
    ("Brema", 152): ("Bremen", "Brema (p. 152)", 53.08, 8.8),
    ("Ysland", 162): ("Iceland", "Iceland, colonised by the Norwegians (p. 162)", 64.9, -18.6),
    ("Fareie", 162): ("the Faroe Islands", "the Faroes, discovered by the Normans in 861 (p. 162)", 62.0, -6.9),
    ("Orcades", 161): ("Orkney", "the Orkneys (p. 161)", 59.0, -3.0),
    ("Noreya", 158): ("Norway", "Norway alone is named, under the form Noreya (p. 158)", 61.0, 9.0),
    ("Ganzmir", 158): (None, "Ganzmir: its meaning we cannot divine (p. 158)", None, None),
    ("Cinocephales", 159): (None, "the dog-headed race (p. 159)", None, None),
    ("S. Andr", 171): ("St Andrews", "St Andrews, an episcopal see (p. 171)", 56.34, -2.8),
    ("Berwic", 171): ("Berwick-upon-Tweed", "Berwic, an important fortress in the period of the Scottish wars (p. 171)", 55.77, -2.0),
    ("Rokesburg", 171): ("Roxburgh", "Roxburgh, another border fortress of importance (p. 171)", 55.6, -2.45),
    ("Edenburgh", 171): ("Edinburgh", "Edenburgh (p. 171)", 55.95, -3.19),
    ("Castello Novo", 169): ("Newcastle upon Tyne", "Castello Novo, Newcastle-on-Tyne (p. 169)", 54.97, -1.61),
    ("Carlua", 169): ("Carlisle", "Carlisle; the form of the name is peculiar (p. 169)", 54.89, -2.93),
    ("Durem", 169): ("Durham", "Durham, with its cathedral church appropriately placed on a hill (p. 169)", 54.78, -1.57),
    ("Eboracum", 169): ("York", "Eboracum, York (p. 169)", 53.96, -1.08),
    ("Kircham", 169): ("Kirkham Priory", "a priory of no great fame ... on the Derwent, six miles below Malton (p. 169)", 54.08, -0.88),
    ("Cestria", 169): ("Chester", "Chester (p. 169)", 53.19, -2.89),
    ("Snotingham", 169): ("Nottingham", "the original form of Nottingham (p. 169)", 52.95, -1.15),
    ("Lincoln", 168): ("Lincoln", "Lincoln, with its cathedral duly depicted on an elevation (p. 168 to 169)", 53.23, -0.54),
    ("Ely", 168): ("Ely", "Ely, represented as on an island in the Nen (p. 168)", 52.4, 0.26),
    ("Norhanton", 168): ("Northampton", "Northampton (p. 168)", 52.24, -0.9),
    ("Colcestria", 168): ("Colchester", "Colchester (p. 168)", 51.89, 0.9),
    ("Londonia", 168): ("London", "London, represented by a castellated structure of fair proportions (p. 168)", 51.51, -0.13),
    ("Oxeford", 168): ("Oxford", "Oxford, in the 13th century the seat of a university (p. 168)", 51.75, -1.26),
    ("Wircestr", 169): ("Worcester", "Worcester, an episcopal see (p. 169)", 52.19, -2.22),
    ("Hreford", 169): ("Hereford", "Hereford (p. 169)", 52.06, -2.72),
    ("Glearum", 169): ("Gloucester", "evidently intended for Gloucester (p. 170)", 51.86, -2.24),
    ("Bathe", 170): ("Bath", "Bath, an episcopal see at the period of the map (p. 170)", 51.38, -2.36),
    ("Glestonia", 170): ("Glastonbury", "Glastonbury, the seat of the most famous monastery in Britain (p. 170)", 51.15, -2.71),
    ("Canturia", 170): ("Canterbury", "Canterbury (p. 170)", 51.28, 1.08),
    ("Wintona", 170): ("Winchester", "Winchester (p. 170)", 51.06, -1.31),
    ("Cadan", 170): ("Caen (misplaced in England)", "Caen, which has been, by a strange blunder, transferred from the southern to the northern side of the channel (p. 170)", 49.18, -0.37),
    ("Excestria", 170): ("Exeter", "Exeter, an episcopal see (p. 170)", 50.72, -3.53),
    ("Carnarvan", 171): ("Caernarfon", "Carnarvan (p. 171)", 53.14, -4.27),
    ("Cunwey", 171): ("Conwy", "Cunwey, Conway (p. 171)", 53.28, -3.83),
    ("Snawedon", 171): ("Snowdon", "Snowdon, a district name answering to our Snowdonia (p. 171)", 53.07, -4.08),
    ("Man", 172): ("the Isle of Man", "Man (p. 172)", 54.23, -4.53),
    ("Divelin", 172): ("Dublin", "Dublin (p. 172)", 53.35, -6.26),
    ("Bencur", 172): ("Bangor, County Down", "Bangor, another ecclesiastical town of note (p. 172)", 54.66, -5.67),
    ("Celdara", 172): ("Kildare", "Kildare, the city of St Bridget (p. 172)", 53.16, -6.91),
    ("Arhmata", 172): ("Armagh", "Armagh, the city of St Patrick (p. 172)", 54.35, -6.65),
}

# Medieval names in the Europe chapters (step 4 of the rule): places, regions and peoples of the Middle Ages, and
# post-classical forms of names (Aragon, Bavaria's Regensburg, Santiago...). All other unmatched European names count
# as classical, the default. In the British Isles every name counts as medieval except the classical ones listed.
MEDIEVAL_EU = {70, 120, 133, 137, 157, 159, 168, 173, 181, 184, 185, 186, 294, 400, 414, 423, 439, 489, 491, 498, 538,
               568, 582, 627, 628, 648, 677, 688, 701, 744, 786, 792, 824, 843, 850, 856, 900, 969, 1017}
CLASSICAL_BRIT = {174, 481, 981, 574, 922}   # Britannia, Hibernia, the Velabri and Luceni (from Orosius), Thanet (Solinus)

# Gazetteer matches checked by hand and rejected (wrong place of the same or a similar name), by index key.
REJECT_GAZ = {
    # approximate Pleiades spellings that point to another place
    "Achen", "Alani", "Alanus", "Albana", "Albani", "Boetis", "Capadocia", "Cebentia", "Choos", "Delta", "Dorius", "Fasga", "Geneis",
    "Grana", "Heremus", "Hesperus", "Insula", "Lates", "Laude", "Libeum", "Ligria", "Malleus", "Marinia", "Marna", "Mediterraneum",
    "Messia", "Papia", "Pasma", "Petavium", "Samara", "Salze", "Sarta", "Sertos", "Sinus", "Sobas", "Stipa", "Chusta", "Emisa",
    "Pandea", "Thelea", "Terasia", "Stenas",
    # exact names that belong to a different place than the one on the map
    "Canna", "Diospolis", "Hellada", "Lak", "Libia", "Ligeris", "Meroe", "Ophir", "Panda", "Sabaria", "Sala", "Sile", "Sochoth",
    "Yda", "Boreum", "Cana", "Germania", "Nisa", "Neon", "Verona", "Augusta", "Apollonia", "Galata",
    # approximate spellings checked on a second pass
    "Acesines", "Arcbas", "Leona", "Laris", "Magdalum", "Tracianopolis", "Tipassa", "Sabaa", "Ammone", "Gazan", "Eonee", "Membrona", "Aretusa"}
