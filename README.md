# Epsilon Stays

Campgrounds we've stayed in, and **which individual site to ask for** once you get there.

Live at **https://stays.adventuresinepsilon.com/** — a companion to
[Epsilon Adventures](https://adventuresinepsilon.com).

## Why it exists

Plenty of sites will tell you a campground is nice. Almost none will tell you that site 42
floods, that the pedestal at 17 lands on the wrong side, or that the only three sites with a
clear northern sky for Starlink are at the far end of the C loop. That site-level detail is what
this is for.

## The reference rig

Every fit judgment is made against ours:

| | |
|---|---|
| Trailer | 2022 Airstream Globetrotter 23FB Twin — **24 ft** |
| Tow vehicle | 2025 RAM 2500 diesel |
| Combined | **46 ft** |
| Electrical | 30A |

Where a site takes more than 24 ft, the posted or observed maximum is recorded, so these notes
stay useful to rigs bigger than ours.

## Epsilon Approved

A badge, not a category. Most campgrounds here won't have it. It marks the ones we'd go out of
our way to return to.

## How it's built

No CMS, no database. `data/campgrounds.json` holds everything; `build.py` renders static HTML.

```bash
python3 build.py      # regenerate index.html and c/<id>/index.html
./deploy.sh           # rebuild, commit, push
```

See [`data/SCHEMA.md`](data/SCHEMA.md) for every field.

## The one rule

**Never record a value you didn't observe.** Unknown is `null` and renders as an em dash. A
campground guide is only worth publishing if everything in it is true — sparse and honest beats
complete and invented.
