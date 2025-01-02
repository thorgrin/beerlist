#!/usr/bin/env python3

import sys
import json

breweries = {
    'Rodinný pivovar Zichovec': 'Zichovec',
    'NOZIB Special Brews': 'NOZIB',
    'Akciový pivovar Libertas': 'Libertas',
    'Pivovar ': '',
}

beers = []
for line in sys.stdin:
    data = json.loads(line)
    index_beer = data['headers'].index('Pivo')
    index_brewery = data['headers'].index('Pivovar')
    for beer in data['beers']:
        name = beer[index_beer]
        brewery = beer[index_brewery]

        # Make brewery name shorter for a known list
        for full, short in breweries.items():
            brewery = brewery.replace(full, short)

        # Prepend brewery if necessary
        if brewery not in name:
            name = brewery + " " + name

        beers += [name]

print(" | ".join(beers))
