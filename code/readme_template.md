# Signature sports: where the world's niche games are unusually popular

Every country plays football. This study asks which sport each country plays unusually much. From {{meta.clubs|int}} sports clubs and club teams in Wikidata it computes, for every sport and country, a location quotient (the sport's share of the country's clubs divided by its share of the world's) and colours each country by its "signature sport". A pick-a-sport heat map shows where any of {{meta.sports_listed|int}} sports is over-represented, by country and by first-level region; Olympic medal tables and Wikipedia page views are second signals; and a UK map does the same county by county with places to play mapped in OpenStreetMap.

**Interactive version:** https://maps.tristanhotham.com/niche-sports/

**Paper and archived release:** https://doi.org/10.5281/zenodo.23748256

A data study by Dr Tristan Hotham (Independent researcher, ORCID 0000-0003-4931-9349).

## Headline results

- {{signature.n_signature|int}} of the {{signature.n_countries_mapped|int}} countries with at least {{thr.country|int}} clubs have a clear signature sport, and {{signature.n_sports|int}} different sports are a signature somewhere. Football is {{meta.football_share|pct}} of all clubs and the signature in {{signature.football_signature|int}} countries, always with a weak lead.
- The biggest leads: boxing in Uganda ({{sig.UGA.lq|x}} the world average, largely a recording effect), tchoukball in Switzerland ({{sig.CHE.lq|x}}), pesäpallo in Finland ({{sig.FIN.lq|x}}), hurling and camogie in Ireland ({{sig.IRL.lq|x}}), cricket in Sri Lanka ({{sig.LKA.lq|x}}) and Pakistan ({{sig.PAK.lq|x}}). Speedway is Poland's ({{sig.POL.lq|x}}), korfball the Netherlands' ({{sig.NLD.lq|x}}).
- Regional blocks: handball from Tunisia to the Balkans, volleyball from Turkey to Kazakhstan, futsal in Brazil, Iran, South Korea and Ukraine, cycling in Colombia, Ecuador and Venezuela.
- Inside countries: rowing in Gipuzkoa ({{region_top.rowing.0.lq|x}}), hurling in Tipperary ({{region_top.hurling and camogie.0.lq|x}}), roller hockey in Barcelona ({{region_top.roller hockey.0.lq|x}}).
- Check with only the {{wp.clubs|int}} clubs that have a Wikipedia article: {{wp.same_sig|int}} of {{wp.both|int}} countries keep the same signature. Bulk imports show up: the UK's signature moves from target shooting ({{caveat.uk_shooting|int}} clubs) to cricket, Sweden's from minigolf to orienteering.
- Olympic medals agree only loosely with clubs (Spearman's rho {{medals.spearman|f2}}, {{medals.pairs|int}} pairs); pairs high on both include Finland wrestling, Canada curling, Norway skiing, Hungary water polo and Colombia cycling.
- UK: {{uk.features|int}} OpenStreetMap features with a sport tag, merged into {{uk.sites|int}} places to play in {{uk.areas|int}} counties and districts.

Every number is in `data/results.json`, which the page, paper, blog and collage are built from.

## Method in brief

- **Location quotient** LQ = (n_cs / N_c) / (N_s / N): the sport's share of a place's clubs over its share of all clubs. Each place is compared with itself, so differences in how thoroughly places are recorded cancel out (but not differences in which sports are recorded).
- **Minimum counts.** A country needs {{thr.country|int}} clubs to be mapped; a sport needs {{thr.cell|int}} clubs in a country to be a heartland there and {{thr.sport|int}} worldwide to be listed. Regions need {{thr.region|int}} located clubs and {{thr.region_cell|int}} of the sport. UK counties need 300 places to play and 5 of the sport.
- **Cautious ratio.** The signature sport is chosen by the quotient recalculated with the count replaced by the lower end of an exact two-sided 90% Poisson interval (10 clubs count as {{thr.lo10|f1}}, 100 as {{thr.lo100|f1}}), so small counts cannot win by chance. Both figures are published.
- **Clubs.** Wikidata items that are a sports club or sports team (any subclass) with a sport and a country. National sides, delegations, "nation at" entries, team seasons, youth and reserve sides, school and college teams, and commercial motor-racing and esports teams are removed; variants of a sport are merged; a club with k sports counts 1/k for each.
- **UK places to play.** OpenStreetMap features with a sport tag; features of the same sport in the same 0.002 by 0.003 degree grid square (about 220 by 200 m) count as one place.

## Files

| Path | What it is |
|---|---|
| `index.html` | The interactive page (page tables embedded; outlines loaded from `data/geo_*.json`). |
| `header.png` | Social card (1200 by 630). |
| `data/country_sport.csv` | Clubs by country and sport: n, country total, sport total, share, location quotient, cautious ratio, eligibility. |
| `data/country_sport_wikipedia_only.csv` | The same using only clubs with a Wikipedia article. |
| `data/signature_sports.csv`, `data/signature_sports_wikipedia_only.csv` | Each country's signature sport and status. |
| `data/region_sport.csv`, `data/region_signature.csv` | First-level regions (Natural Earth admin 1), located clubs only. |
| `data/sports.csv` | Every sport with its world club count, share, number of countries and colour. |
| `data/olympic_medals.csv` | All-time Olympic medals by present-day country and sport (English Wikipedia), with medal quotients. CC BY-SA 4.0. |
| `data/pageviews_language.csv` | 2025 Wikipedia page views by language edition and sport, with quotients. |
| `data/uk_county_sport.csv`, `data/uk_signature.csv`, `data/uk_sites_niche.csv` | UK places to play by county and sport, county signatures, and the located places for smaller sports. ODbL 1.0. |
| `data/geo_countries.json`, `data/geo_regions.json`, `data/geo_uk.json` | Simplified outlines with label points. |
| `data/results.json` | Every number used anywhere. |
| `code/01_prepare.py` | Reads the Wikidata bundle, flags non-club items. |
| `code/sportmap.py` | Sport merges, drops, colours and thresholds. |
| `code/02_world.py` | World, regional, Wikipedia-only, medal and page view analysis. |
| `code/03_uk.py` | UK OpenStreetMap analysis. |
| `code/04_geometry.py` | Outlines for the page and figures. |
| `code/05_results.py`, `code/05b_stories.py` | Results file and page tables; story cards (with checks against the data). |
| `code/06_build_site.py` | Fills `code/page_template.html` to make `index.html`. |
| `code/07_figures.py`, `code/08_header.py`, `code/09_paper.py`, `code/10_release.py` | Figures, social card, paper PDF, blog post and Zenodo files. |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `release/` | Paper PDF and source, blog post and figures, Zenodo files. |

## Known limits

- These are organised clubs as recorded in Wikidata, not players or spectators. Recording differs by sport: bulk imports inflate some sports in some countries (UK target shooting, Swedish minigolf), and multi-sport clubs are often recorded under football only, hiding sports such as fencing.
- The Wikipedia-only check removes most imports but favours notable clubs.
- Only countries with {{thr.country|int}} or more clubs are mapped, and only {{regions.n_eligible|int}} regions are large enough for the regional view; {{meta.located_share|pct}} of clubs have coordinates.
- Medal tables are all-time and leave out former states; page views are by language, not country.
- OpenStreetMap detail varies by place and by type of facility; a place to play is not a club. Sport England's Active Lives survey does not give small sports at county level and is not used.

## Sources and licences

- Wikidata (CC0 1.0), sports clubs and teams, via the QLever SPARQL endpoint (University of Freiburg), retrieved {{meta.retrieved|raw}}.
- English Wikipedia (CC BY-SA 4.0), "Sport at the Summer Olympics" and "at the Winter Olympics" articles, medal tables.
- Wikimedia pageviews API (CC0), user views, 2025.
- OpenStreetMap contributors (ODbL 1.0), features tagged sport=*, via the Overpass API (overpass-api.de and the maps.mail.ru mirror), retrieved {{uk.retrieved|raw}}.
- Natural Earth 1:50m countries and 1:10m states and provinces (public domain).
- UK counties from Office for National Statistics boundaries via onsvisual/uk-topojson (Open Government Licence v3; contains OS data © Crown copyright and database right).
- Base map tiles on the page © Esri.

Text, figures and derived data: CC BY 4.0, except tables derived from OpenStreetMap (ODbL 1.0) and from Wikipedia medal tables (CC BY-SA 4.0). Code: MIT (see `LICENSE`).

## How to rerun

The raw bundles were gathered in a browser (QLever, MediaWiki, Wikimedia and Overpass APIs) and are read from `NS_DATA` (default `/home/claude/hist/_data18/niche-sports`): `ns_world_wikidata.json.gz`, `ns_extra.json.gz`, `ns_uk_osm.json.gz` and `ne_admin1_s02.geojson`. Python 3 with numpy, pandas, scipy, shapely, pyproj and matplotlib; xelatex for the paper.

```
python3 code/01_prepare.py
python3 code/02_world.py
python3 code/04_geometry.py
python3 code/03_uk.py
python3 code/05_results.py
python3 code/05b_stories.py
python3 code/06_build_site.py
python3 code/07_figures.py
python3 code/08_header.py
python3 code/09_paper.py
python3 code/10_release.py
python3 reddit/collage.py
```

## Citation

Hotham, T. (2026) Signature sports: where the world's niche games are unusually popular. Location quotients of sports clubs in Wikidata and OpenStreetMap, by country, region and UK county. https://doi.org/10.5281/zenodo.23748256

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
