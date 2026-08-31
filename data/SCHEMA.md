# Data schema

`campgrounds.json` holds everything. `build.py` renders the site from it. There is no database and no CMS — edit the JSON, run the build, push.

## Ground rule

**Never write a value you did not observe.** Unknown is `null`, and the build renders `null` as "—" rather than guessing. A campground guide is only worth publishing if every field in it is true. Sparse and honest beats complete and invented.

---

## `meta`

| Field | Notes |
|---|---|
| `site_title` | Rendered in the header |
| `tagline` | Rendered under the title |
| `updated` | `YYYY-MM-DD`, bump on each publish |
| `rig` | The reference rig. Every fit judgment is relative to this. |

## `campgrounds[]`

| Field | Type | Notes |
|---|---|---|
| `id` | string | URL slug, lowercase-hyphenated. Becomes `/c/<id>/` |
| `name` | string | |
| `location` | object | `city`, `region` (state/province), `country`, `lat`, `lon` |
| `type` | enum | `state_park`, `national_park`, `coe`, `county`, `city`, `private`, `membership`, `harvest_hosts`, `fairgrounds`, `boondock`, `other` |
| `website` | string/null | |
| `phone` | string/null | |
| `reservation_system` | string/null | e.g. `Recreation.gov`, `ReserveAmerica`, `first-come`, `direct` |
| `season` | string/null | e.g. `May–Oct` |
| `price_range` | string/null | e.g. `$38–52` — include currency for Canada |
| `epsilon_approved` | bool/null | The badge. Reserve it. `null` until judged. |
| `overall` | string | The verdict paragraph. Plain, honest, useful to a stranger. |
| `amenities` | object | `dump`, `potable_water`, `laundry`, `showers` (bool/null); `wifi_quality`, `cell_carrier`, `cell_bars` |
| `stays[]` | array | `arrive`, `depart` (`YYYY-MM-DD`), `status` (`stayed` \| `planned`), `occasion` |
| `sites[]` | array | See below |

## `sites[]`

The heart of it — the part nobody else publishes.

| Field | Type | Notes |
|---|---|---|
| `number` | string | Site number as posted |
| `site_type` | enum/null | `back_in`, `pull_through` |
| `max_length_ft` | int/null | Posted or observed maximum. Record it even when far larger than 24. |
| `fits_our_rig` | bool/null | Against 24 ft trailer / 46 ft combined |
| `pad_surface` | string/null | `gravel`, `paved`, `dirt`, `grass` |
| `levelness` | string/null | `level`, `minor blocks`, `significant blocks`, `poor` |
| `electric` | enum/null | `50A`, `30A`, `20A`, `none` |
| `water` | bool/null | |
| `sewer` | bool/null | |
| `utilities_side` | enum/null | `street`, `curb` — which side the pedestal lands on |
| `solar_exposure` | enum/null | `open`, `partial`, `shaded` |
| `starlink_sky` | enum/null | `clear`, `partial`, `blocked` |
| `afternoon_sun` | string/null | Which way the awning side faces, and whether that's shade or an oven |
| `noise` | string/null | Road, rail, generator hours, neighbours |
| `to_bathhouse_ft` | int/null | |
| `verdict` | string | Would you take this site again, and why |
| `notes` | string | Anything else |
| `photos[]` | array | Relative paths under `assets/photos/` or full URLs |

## Adding a stay

1. Add or find the campground object
2. Append to `stays[]`
3. Add one `sites[]` entry per site you actually occupied or scouted well enough to judge
4. Set `epsilon_approved` if it earned it
5. Bump `meta.updated`
6. `./deploy.sh`

---

## Campground maps

Four optional fields on each campground record:

| Field | Notes |
|---|---|
| `map_file` | Repo-relative path, e.g. `assets/maps/<id>.png`. Only when the map may lawfully be redistributed. |
| `map_url` | The official page the map lives on. Always safe to set. |
| `map_source` | Who made it, e.g. `National Park Service` |
| `map_license` | `public-domain-us-gov`, `permission-granted`, or `link-only` |

**The licensing rule.** Maps produced by the National Park Service, the Forest Service, the Corps
of Engineers, BLM and other U.S. federal agencies are public domain and can be copied into the
repo and displayed. **Maps from state parks, private campgrounds, KOA, Harvest Hosts and
commercial guide sites are copyrighted** — set `map_url` only and leave `map_file` null. The
build renders an inline map when `map_file` is present and a plain outbound link when it isn't.

Where a map exists but neither field is set, it simply doesn't render. Worth filling in over time.
