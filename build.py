#!/usr/bin/env python3
"""Build the Epsilon Stays static site from data/campgrounds.json.

Usage: python3 build.py
Outputs: index.html, c/<id>/index.html
"""

import json
import html
import os
import shutil
from datetime import date

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data", "campgrounds.json")

TYPE_LABELS = {
    "state_park": "State Park",
    "national_park": "National Park",
    "coe": "Corps of Engineers",
    "county": "County",
    "city": "City",
    "private": "Private",
    "membership": "Membership",
    "harvest_hosts": "Harvest Hosts",
    "fairgrounds": "Fairgrounds",
    "boondock": "Boondock",
    "other": "Other",
}


def esc(v):
    return html.escape(str(v)) if v is not None else ""


def dash(v):
    """Render an unknown value as an em dash rather than inventing one."""
    if v is None or v == "":
        return '<span class="unknown">&mdash;</span>'
    if v is True:
        return "Yes"
    if v is False:
        return "No"
    return esc(v)


def head(title, depth=0):
    up = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<link rel="stylesheet" href="{up}assets/css/site.css">
</head>
<body>
"""


def site_header(meta, depth=0):
    up = "../" * depth
    rig = meta["rig"]
    return f"""<header class="masthead">
  <div class="wrap">
    <a class="brand" href="{up}index.html">{esc(meta['site_title'])}</a>
    <p class="tagline">{esc(meta['tagline'])}</p>
    <p class="rig">Our rig: <strong>{rig['trailer_ft']} ft trailer</strong> &middot;
       <strong>{rig['combined_ft']} ft combined</strong> &middot; {esc(rig['electrical'])}
       <span class="rig-detail">({esc(rig['trailer'])} behind a {esc(rig['tow_vehicle'])})</span></p>
    <p class="home-link"><a href="https://adventuresinepsilon.com">&larr; Epsilon Adventures</a></p>
  </div>
</header>
"""


def footer(meta):
    return f"""<footer class="foot">
  <div class="wrap">
    <p>Updated {esc(meta['updated'])} &middot; part of
       <a href="https://adventuresinepsilon.com">Epsilon Adventures</a></p>
    <p class="fine">Every judgment here is ours, made against a {meta['rig']['trailer_ft']} ft trailer.
       Campgrounds change &mdash; check the last-stayed date before you trust a note.</p>
  </div>
</footer>
</body>
</html>
"""


def has_stayed(cg):
    return any(s.get("status") == "stayed" for s in cg.get("stays", []))


def last_stayed(cg):
    dates = [s.get("depart") or s.get("arrive")
             for s in cg.get("stays", []) if s.get("status") == "stayed"]
    dates = [d for d in dates if d]
    return max(dates) if dates else None


def fitting_sites(cg):
    return [s for s in cg.get("sites", []) if s.get("fits_our_rig") is True]


def build_index(data):
    meta, cgs = data["meta"], data["campgrounds"]
    cards = []
    for cg in sorted(cgs, key=lambda c: c["name"]):
        ls = last_stayed(cg)
        stayed = has_stayed(cg)
        loc = cg["location"]
        where = ", ".join(x for x in [loc.get("city"), loc.get("region")] if x)
        badge = '<span class="badge">Epsilon Approved</span>' if cg.get("epsilon_approved") else ""
        nsites = len(cg.get("sites", []))
        nfit = len(fitting_sites(cg))
        status = "stayed" if stayed else "planned"
        cards.append(f"""  <article class="card" data-type="{esc(cg.get('type',''))}"
      data-region="{esc(loc.get('region',''))}"
      data-approved="{'1' if cg.get('epsilon_approved') else '0'}"
      data-status="{status}"
      data-name="{esc(cg['name']).lower()}">
    <h2><a href="c/{esc(cg['id'])}/index.html">{esc(cg['name'])}</a> {badge}</h2>
    <p class="meta">{esc(where)} &middot; {esc(TYPE_LABELS.get(cg.get('type'), cg.get('type') or ''))}</p>
    <p class="meta">{nsites} site{'s' if nsites != 1 else ''} noted{f' &middot; {nfit} fit our rig' if nfit else ''}
       &middot; {('last stayed ' + esc(ls)) if ls else ('stayed &mdash; dates not recorded' if stayed else '<em>not yet stayed</em>')}</p>
    <p class="excerpt">{esc((cg.get('overall') or '')[:180])}</p>
    {'<p class="meta has-map">&#9906; Campground map available</p>' if (cg.get('map_file') or cg.get('map_url')) else ''}
  </article>""")

    regions = sorted({c["location"].get("region") for c in cgs if c["location"].get("region")})
    types = sorted({c.get("type") for c in cgs if c.get("type")})
    region_opts = "".join(f'<option value="{esc(r)}">{esc(r)}</option>' for r in regions)
    type_opts = "".join(
        f'<option value="{esc(t)}">{esc(TYPE_LABELS.get(t, t))}</option>' for t in types)

    return head("Epsilon Stays") + site_header(meta) + f"""
<main class="wrap">
  <section class="intro">
    <p>A running record of the campgrounds we've stayed in and &mdash; the part that's usually
       missing &mdash; <strong>which individual site to ask for</strong> once you get there.</p>
  </section>

  <section class="controls">
    <input type="search" id="q" placeholder="Search campgrounds&hellip;" aria-label="Search">
    <select id="region"><option value="">All states / provinces</option>{region_opts}</select>
    <select id="type"><option value="">All types</option>{type_opts}</select>
    <label class="check"><input type="checkbox" id="approved"> Epsilon Approved only</label>
    <label class="check"><input type="checkbox" id="stayedonly"> Stayed only</label>
  </section>

  <section id="list" class="cards">
{chr(10).join(cards)}
  </section>
  <p id="empty" class="empty" hidden>Nothing matches those filters.</p>
</main>

<script>
(function () {{
  var q = document.getElementById('q'),
      region = document.getElementById('region'),
      type = document.getElementById('type'),
      approved = document.getElementById('approved'),
      stayedonly = document.getElementById('stayedonly'),
      cards = Array.prototype.slice.call(document.querySelectorAll('.card')),
      empty = document.getElementById('empty');

  function apply() {{
    var term = q.value.trim().toLowerCase(), shown = 0;
    cards.forEach(function (c) {{
      var ok = true;
      if (term && c.dataset.name.indexOf(term) === -1) ok = false;
      if (region.value && c.dataset.region !== region.value) ok = false;
      if (type.value && c.dataset.type !== type.value) ok = false;
      if (approved.checked && c.dataset.approved !== '1') ok = false;
      if (stayedonly.checked && c.dataset.status !== 'stayed') ok = false;
      c.hidden = !ok;
      if (ok) shown++;
    }});
    empty.hidden = shown !== 0;
  }}
  [q, region, type, approved, stayedonly].forEach(function (el) {{
    el.addEventListener('input', apply);
    el.addEventListener('change', apply);
  }});
}})();
</script>
""" + footer(meta)


def site_row(s, rig_ft):
    fits = s.get("fits_our_rig")
    cls = "fits-yes" if fits is True else ("fits-no" if fits is False else "fits-unk")
    maxlen = s.get("max_length_ft")
    maxlen_txt = f"{maxlen} ft" if maxlen else None
    hookups = []
    if s.get("electric"):
        hookups.append(esc(s["electric"]))
    if s.get("water"):
        hookups.append("W")
    if s.get("sewer"):
        hookups.append("S")
    hookup_txt = " / ".join(hookups) if hookups else None

    return f"""<article class="site {cls}">
  <h3>Site {esc(s.get('number'))}</h3>
  <dl class="sitegrid">
    <div><dt>Fits our {rig_ft} ft</dt><dd>{dash(fits)}</dd></div>
    <div><dt>Max length</dt><dd>{dash(maxlen_txt)}</dd></div>
    <div><dt>Type</dt><dd>{dash((s.get('site_type') or '').replace('_',' ') or None)}</dd></div>
    <div><dt>Hookups</dt><dd>{dash(hookup_txt)}</dd></div>
    <div><dt>Pad</dt><dd>{dash(s.get('pad_surface'))}</dd></div>
    <div><dt>Level</dt><dd>{dash(s.get('levelness'))}</dd></div>
    <div><dt>Utilities side</dt><dd>{dash(s.get('utilities_side'))}</dd></div>
    <div><dt>Solar</dt><dd>{dash(s.get('solar_exposure'))}</dd></div>
    <div><dt>Starlink sky</dt><dd>{dash(s.get('starlink_sky'))}</dd></div>
    <div><dt>Afternoon sun</dt><dd>{dash(s.get('afternoon_sun'))}</dd></div>
    <div><dt>Noise</dt><dd>{dash(s.get('noise'))}</dd></div>
    <div><dt>To bathhouse</dt><dd>{dash(str(s['to_bathhouse_ft']) + ' ft' if s.get('to_bathhouse_ft') else None)}</dd></div>
  </dl>
  {'<p class="verdict">' + esc(s['verdict']) + '</p>' if s.get('verdict') else ''}
  {'<p class="notes">' + esc(s['notes']) + '</p>' if s.get('notes') else ''}
</article>"""


def build_campground(data, cg):
    meta = data["meta"]
    rig_ft = meta["rig"]["trailer_ft"]
    loc = cg["location"]
    where = ", ".join(x for x in [loc.get("city"), loc.get("region"), loc.get("country")] if x)
    badge = '<span class="badge">Epsilon Approved</span>' if cg.get("epsilon_approved") else ""
    a = cg.get("amenities", {})

    mf, mu = cg.get("map_file"), cg.get("map_url")
    if mf:
        up = "../../"
        credit = esc(cg.get("map_source") or "")
        official = (f'<p class="meta">Official page: <a href="{esc(mu)}">{esc(mu)}</a></p>' if mu else "")
        map_section = f"""<section>
    <h2>Campground map</h2>
    <p class="maplink"><a href="{up}{esc(mf)}">Open the full-size campground map</a></p>
    <a href="{up}{esc(mf)}"><img class="cgmap" src="{up}{esc(mf)}" alt="Campground map" loading="lazy"></a>
    <p class="fine">Map: {credit}. Public domain (U.S. Government work).</p>
    {official}
  </section>"""
    elif mu:
        map_section = f"""<section>
    <h2>Campground map</h2>
    <p class="maplink"><a href="{esc(mu)}">View the campground map</a></p>
    <p class="fine">Hosted by the campground &mdash; linked rather than copied.</p>
  </section>"""
    else:
        map_section = ""

    stays = "".join(
        f"<li>{esc(s.get('arrive'))}{' &ndash; ' + esc(s['depart']) if s.get('depart') else ''} "
        f"&middot; <span class=\"tag\">{esc(s.get('status'))}</span>"
        f"{' &middot; ' + esc(s['occasion']) if s.get('occasion') else ''}</li>"
        for s in cg.get("stays", []))

    sites = cg.get("sites", [])
    sites_html = ("\n".join(site_row(s, rig_ft) for s in sites) if sites
                  else '<p class="empty">No site-level notes recorded yet.</p>')

    return head(f"{cg['name']} — Epsilon Stays", depth=2) + site_header(meta, depth=2) + f"""
<main class="wrap detail">
  <p class="back"><a href="../../index.html">&larr; All stays</a></p>
  <h1>{esc(cg['name'])} {badge}</h1>
  <p class="meta">{esc(where)} &middot; {esc(TYPE_LABELS.get(cg.get('type'), cg.get('type') or ''))}</p>

  {'<section class="overall"><p>' + esc(cg['overall']) + '</p></section>' if cg.get('overall') else ''}

  <section>
    <h2>The campground</h2>
    <dl class="sitegrid">
      <div><dt>Reservations</dt><dd>{dash(cg.get('reservation_system'))}</dd></div>
      <div><dt>Season</dt><dd>{dash(cg.get('season'))}</dd></div>
      <div><dt>Price</dt><dd>{dash(cg.get('price_range'))}</dd></div>
      <div><dt>Phone</dt><dd>{dash(cg.get('phone'))}</dd></div>
      <div><dt>Dump station</dt><dd>{dash(a.get('dump'))}</dd></div>
      <div><dt>Potable water</dt><dd>{dash(a.get('potable_water'))}</dd></div>
      <div><dt>Showers</dt><dd>{dash(a.get('showers'))}</dd></div>
      <div><dt>Laundry</dt><dd>{dash(a.get('laundry'))}</dd></div>
      <div><dt>Wi-Fi</dt><dd>{dash(a.get('wifi_quality'))}</dd></div>
      <div><dt>Cell</dt><dd>{dash((str(a['cell_carrier']) + ' ' + str(a.get('cell_bars') or '')).strip() if a.get('cell_carrier') else None)}</dd></div>
    </dl>
    {'<p><a href="' + esc(cg['website']) + '">Campground website</a></p>' if cg.get('website') else ''}
  </section>

  {map_section}

  <section>
    <h2>Our stays</h2>
    <ul class="stays">{stays or '<li>—</li>'}</ul>
  </section>

  <section>
    <h2>Sites</h2>
    {sites_html}
  </section>
</main>
""" + footer(meta)


def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    out = os.path.join(ROOT, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(build_index(data))
    print("wrote index.html")

    cdir = os.path.join(ROOT, "c")
    if os.path.isdir(cdir):
        shutil.rmtree(cdir)
    for cg in data["campgrounds"]:
        d = os.path.join(cdir, cg["id"])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
            f.write(build_campground(data, cg))
        print(f"wrote c/{cg['id']}/index.html")

    print(f"done — {len(data['campgrounds'])} campgrounds")


if __name__ == "__main__":
    main()
