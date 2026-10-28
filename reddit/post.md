## Title

[OC] Every country's "signature sport": not the sport it plays most (football, almost everywhere) but the one it plays most above the world average, from 99,246 sports clubs in Wikidata. Pesäpallo in Finland is 70x the world average, tchoukball in Switzerland 95x, hurling in Ireland 61x

## Body (optional)

I took every sports club and club team in Wikidata, removed national sides, delegations and school teams, and for each country divided each sport's share of its clubs by that sport's share of the world's clubs. Comparing a country with itself cancels out how well it is recorded. A sport needs 10 clubs in a country to count, and the winner is picked with a cautious version of the ratio so tiny counts cannot win. 92 countries have a clear signature, spread over 34 sports; speedway is Poland's (26x) and korfball the Netherlands' (16x). Caveat: bulk imports skew a few countries (the UK's 851 target shooting clubs); counting only clubs with a Wikipedia article, 71 of 87 countries keep the same signature.

Interactive version, with a pick-a-sport map and a UK county map: https://maps.tristanhotham.com/niche-sports/

## Source comment

Source: Wikidata sports clubs and teams (instances of sports club Q847017 or sports team Q12973014 and subclasses, with sport and country), queried through the QLever endpoint, 2026-10-28 (CC0); all-time Olympic medal tables from English Wikipedia "Sport at the Summer/Winter Olympics" articles (CC BY-SA 4.0); Wikipedia pageviews from the Wikimedia API, 2025 (CC0); UK places to play from OpenStreetMap features tagged sport=*, via the Overpass API (© OpenStreetMap contributors, ODbL); outlines from Natural Earth (public domain) and ONS boundaries (OGL v3).

Tools: Python (pandas, NumPy, SciPy, Shapely, pyproj, matplotlib).

Interactive: https://maps.tristanhotham.com/niche-sports/
Blog post: https://blog.tristanhotham.com/2026/10/28/niche-sports/
Paper: https://doi.org/10.5281/zenodo.23748256
