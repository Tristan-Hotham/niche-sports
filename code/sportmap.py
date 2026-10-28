"""Shared definitions: how Wikidata sport items are merged into the sports used here, which are dropped,
the colour of each sport, and the thresholds. Imported by the analysis, figure and collage scripts."""

# Variants merged into one sport (Wikidata QID -> canonical QID)
MERGE = {
    "Q606060": "Q2736", "Q31930761": "Q2736", "Q28954": "Q2736",                 # women's / men's / indoor football
    "Q2887217": "Q5372", "Q46343203": "Q5372", "Q210550": "Q5372",               # basketball variants, 3x3
    "Q3609": "Q53121", "Q2215841": "Q53121", "Q221635": "Q53121", "Q520611": "Q53121", "Q335638": "Q53121",
    "Q111721834": "Q53121",                                                      # cycling disciplines
    "Q130949": "Q7718x", "Q15621650": "Q7718x", "Q216613": "Q7718x", "Q179687": "Q7718x", "Q186222": "Q7718x",
    "Q7718": "Q7718x", "Q201965": "Q7718x", "Q93858": "Q7718x", "Q189472": "Q7718x",   # skiing (all disciplines)
    "Q3312129": "Q542", "Q105674": "Q542", "Q500050": "Q542", "Q10572883": "Q542",   # athletics
    "Q6388": "Q31920", "Q631004": "Q31920",                                      # swimming
    "Q326827": "Q43450", "Q61465": "Q43450", "Q465014": "Q43450", "Q1049443": "Q43450",  # gymnastics
    "Q5378": "Q5849", "Q270102": "Q5849", "Q124354356": "Q5849",                 # rugby union, sevens, walking rugby
    "Q20856109": "Q213934",                                                      # canoeing
    "Q20900739": "Q8418", "Q1402543": "Q8418",                                   # handball
    "Q20892731": "Q1734",                                                        # volleyball
    "Q3440462": "Q1748406",                                                      # roller hockey
    "Q17165362": "Q192431", "Q193654": "Q192431",                                # speed skating
    "Q192520": "Q14085739", "Q8046440": "Q14085739", "Q191051": "Q14085739",     # sailing
    "Q3778516": "Q204632",                                                       # ladies' Gaelic football
    "Q601972": "Q213711",                                                        # camogie -> hurling
    "Q16996906": "Q41323", "Q1358545": "Q41323", "Q3747845": "Q41323", "Q692853": "Q41323",  # American football
    "Q950138": "Q5375", "Q8031140": "Q5375",                                     # cricket
    "Q2302906": "Q185851", "Q3003786": "Q185851",                                # lacrosse
    "Q3177899": "Q172809",                                                       # bowling -> ten-pin
    "Q6383440": "Q706199",                                                       # kegel -> nine-pin bowling
    "Q917562": "Q3341285",                                                       # carom -> cue sports
    "Q2483334": "Q212845",                                                       # Valencian pilota -> pelota
    "Q11888296": "Q206989",                                                      # pistol shooting
    "Q838089": "Q42486",                                                         # amateur wrestling
    "Q2631720": "Q32112",                                                        # professional boxing
}
NAMES = {"Q7718x": "skiing", "Q53121": "cycling", "Q31920": "swimming", "Q2736": "football", "Q41323": "American football",
         "Q1748406": "roller hockey", "Q213934": "canoeing", "Q14085739": "sailing", "Q172809": "ten-pin bowling",
         "Q706199": "nine-pin bowling", "Q212845": "Basque pelota", "Q206989": "shooting", "Q5849": "rugby union",
         "Q213711": "hurling and camogie", "Q204632": "Gaelic football", "Q1295867": "pesäpallo", "Q754796": "minigolf",
         "Q1070325": "ice stock sport", "Q192431": "speed skating", "Q3341285": "cue sports", "Q750080": "speedway",
         "Q29358": "orienteering", "Q50776": "Australian rules football", "Q192937": "korfball", "Q183018": "bandy",
         "Q206763": "floorball", "Q1050588": "fistball", "Q659707": "tchoukball", "Q148636": "kabaddi", "Q850256": "shinty",
         "Q1972786": "ringette", "Q376951": "bolo palma", "Q1826965": "motoball", "Q895060": "bocce", "Q189317": "pétanque",
         "Q171401": "futsal", "Q210778": "beach soccer", "Q4543": "beach volleyball", "Q12100": "fencing", "Q134211": "polo",
         "Q185851": "lacrosse", "Q136851": "curling", "Q231200": "netball", "Q7707": "water polo", "Q10962": "rugby league",
         "Q5375": "cricket", "Q5369": "baseball", "Q41466": "ice hockey", "Q8418": "handball", "Q1455": "field hockey",
         "Q7291": "badminton", "Q5372": "basketball", "Q1734": "volleyball", "Q542": "athletics", "Q847": "tennis",
         "Q5377": "golf", "Q3930": "table tennis", "Q43450": "gymnastics", "Q159354": "rowing", "Q32112": "boxing",
         "Q11420": "judo", "Q11419": "karate", "Q38108": "figure skating", "Q10980": "triathlon", "Q42486": "wrestling",
         "Q36389": "taekwondo", "Q7735": "diving", "Q738622": "dancesport", "Q946171": "inline hockey",
         "Q248534": "Canadian football", "Q83462": "weightlifting", "Q166788": "biathlon", "Q133201": "squash",
         "Q108429": "archery", "Q61391": "cheerleading", "Q902378": "equestrian sport", "Q131471": "darts",
         "Q1582389": "padel", "Q43114": "aikido", "Q177275": "bobsleigh", "Q5386": "motor racing", "Q22857": "climbing",
         "Q244700": "ultimate", "Q12014035": "hiking", "Q172809x": "", "Q273285": "luge", "Q667692": "Nordic walking",
         "Q180692": "artistic swimming", "Q178678": "kickboxing", "Q163770": "jujutsu", "Q43080": "roller derby",
         "Q1707432": "roller skating", "Q5367": "motorsport", "Q36908": "mountaineering", "Q876737": "disc golf",
         "Q1443621": "artistic roller skating", "Q1128216": "wheelchair basketball", "Q895471": "bowls",
         "Q171038": "softball", "Q193387": "croquet", "Q690676": "canoe polo", "Q1672856": "Gaelic handball",
         "Q186190": "skeleton", "Q114466": "mixed martial arts", "Q178131": "snowboarding", "Q215184": "BMX",
         "Q170931": "kendo", "Q187916": "horse racing", "Q159452": "capoeira", "Q483693": "parkour", "Q213796": "powerlifting",
         "Q1482312": "synchronised skating", "Q215641": "aerobics", "Q8099087": "cycle ball", "Q2280583": "krachtbal",
         "Q1549761": "prellball", "Q28378697": "rinkball", "Q567014": "wheel gymnastics", "Q32485": "modern pentathlon",
         "Q624161": "gliding", "Q14300548": "skating", "Q6034982": "inline skating", "Q46654": "German ju-jutsu",
         "Q337979": "strength sport"}
# Wikidata sport values that are not one sport, or not physical sport, and are left out
DROP = {"Q204686", "Q61065", "Q814517", "Q11417", "Q7128792", "Q820236", "Q107031718", "Q573766", "Q5146583", "Q484937",
        "Q644628", "Q300920", "Q718", "Q1293", "Q188966", "Q7272708", "Q212434", "Q349", "Q11598537", "Q1741917",
        "Q28910752", "Q2164355", "Q328716", "Q752021", "Q11639", "Q229680", "Q283534", "Q1719546", "Q179643", "Q3505012",
        "Q2413978", "Q2261949", "Q14300548", "Q337979", "Q12014035", "Q667692", "Q36908", "Q484937"}

# Thresholds (stated on the page and in the paper)
MIN_COUNTRY_CLUBS = 100     # a country needs at least this many clubs in Wikidata to be mapped
MIN_CELL = 10               # a sport needs at least this many clubs in a country before it can be called a heartland
MIN_SPORT_WORLD = 30        # a sport needs at least this many clubs worldwide to be in the list
MIN_REGION_CLUBS = 50       # region (admin 1) needs this many located clubs
MIN_REGION_CELL = 8         # and a sport this many located clubs in the region
CONF = 0.90                 # the cautious ratio uses the lower end of a two-sided 90% Poisson interval

# One bold colour per sport that can be a signature sport (others fall back to a neutral)
COLOURS = {
    "football": "#7A8C5A", "bandy": "#1F6FD6", "hurling and camogie": "#1C9E5B", "Gaelic football": "#0F7A47",
    "Australian rules football": "#D9481C", "korfball": "#F08A00", "pesäpallo": "#2A4BA8", "floorball": "#6C3FC9",
    "handball": "#E0362C", "ice hockey": "#3C8FD9", "baseball": "#C4223B", "American football": "#7B3F1D",
    "cricket": "#5DA639", "rugby league": "#8F1D5E", "rugby union": "#2E7D32", "volleyball": "#F2B705",
    "basketball": "#F26B1D", "field hockey": "#008C8C", "badminton": "#B5338A", "fencing": "#C2185B",
    "netball": "#E5559B", "cycling": "#FFB000", "skiing": "#4FA3E0", "curling": "#5A6BD8", "orienteering": "#E2632A",
    "minigolf": "#7DB33A", "water polo": "#1A9FC4", "futsal": "#A2C523", "lacrosse": "#7E57C2", "speedway": "#B03A2E",
    "shooting": "#6D6E2E", "table tennis": "#D7263D", "tennis": "#9BBF2A", "golf": "#3F8F3F", "gymnastics": "#C2459E",
    "athletics": "#E35D22", "swimming": "#2196C8", "rowing": "#225F9C", "judo": "#4B4B9E", "polo": "#9C6B30",
    "shinty": "#3E7C3A", "Basque pelota": "#C0392B", "kabaddi": "#E67E22", "roller hockey": "#8E44AD",
    "Canadian football": "#A0522D", "ice stock sport": "#5D8AA8", "nine-pin bowling": "#B8860B", "chess": "#555",
    "biathlon": "#3E6FB0", "beach soccer": "#E4A11B", "tchoukball": "#16A085", "fistball": "#D35400",
    "motorsport": "#5F5F5F", "boxing": "#A61E22", "sailing": "#1F78B4", "cue sports": "#2C7A3F", "dancesport": "#D6336C",
    "speed skating": "#3A7DC9", "figure skating": "#7FA8D9", "softball": "#E5533C", "triathlon": "#2BA59A",
    "karate": "#9A3B3B", "wrestling": "#8C4A2F", "taekwondo": "#3949AB", "equestrian sport": "#7D5A3A",
    "canoeing": "#2F8F83", "inline hockey": "#5C6BC0", "bowls": "#6B8E23", "croquet": "#558B2F", "darts": "#B23A48",
    "padel": "#00897B", "pétanque": "#A1887F", "bocce": "#8D6E63", "diving": "#039BE5", "weightlifting": "#6D4C41",
    "archery": "#AD1457", "squash": "#00838F", "cheerleading": "#EC407A", "bobsleigh": "#455A64", "luge": "#546E7A",
    "climbing": "#8D6E63", "ultimate": "#26A69A", "artistic swimming": "#4DD0E1", "roller derby": "#AB47BC",
    # UK (OpenStreetMap) names
    "Gaelic games": "#1C9E5B", "equestrian": "#8B5A2B", "horse racing": "#6D4C41", "free flying": "#29B6F6", "rounders": "#F9A825",
    "fishing": "#00796B", "karting": "#616161", "water sports": "#0288D1", "real tennis": "#6A1B9A", "fives": "#AD1457",
    "rackets": "#4E342E", "stoolball": "#C62828", "skittles": "#8D6E63", "skateboarding": "#455A64", "greyhound racing": "#795548",
    "pickleball": "#43A047", "ice skating": "#4FC3F7", "model flying": "#78909C", "racquet sports": "#5E35B1", "trampolining": "#EC407A",
    "martial arts": "#B71C1C", "ten-pin bowling": "#B8860B", "minigolf": "#7DB33A", "dog agility": "#A1887F", "surfing": "#26C6DA", "gliding": "#90A4AE", "parachuting": "#7986CB",
}
NEUTRAL = "#8A8F98"


def name(q, label):
    return NAMES.get(q, label)
