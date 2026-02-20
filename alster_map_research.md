# Hamburg Alster & Marathon Map Research

## Coordinate System

All SVG coordinates use this projection:
- **Origin**: lat=53.55, lon=9.99
- **Scale**: 10,000 SVG units per degree of latitude
- **Longitude correction**: multiplied by 0.594 (cos of latitude ~53.567) to preserve proportions
- **Y-axis**: inverted (negative = north/up in SVG)
- **Conversion formula**:
  ```
  x = (lon - 9.99) * 5940
  y = -(lat - 53.55) * 10000
  ```

For a full-marathon map, use viewBox: `"-575 -748 902 828"`
For an Alster-focused map, use viewBox: `"-120 -320 300 340"`

---

## 1. Binnenalster (Inner Alster)

**Real dimensions**: ~570m x 567m, area 0.2 km^2
**Shape**: Roughly diamond/rhombus shape, oriented NE-SW. The south-west corner has a pointed end (Jungfernstieg area), the north side connects to the Außenalster via bridges.

### SVG Path (from OpenStreetMap relation 6693624)

```svg
<path d="M 25.5 -28.5 L 20.7 -33.8 L 14.4 -40.7 L 12.3 -43.3 L 12.0 -43.4 L 8.3 -47.4 L 9.1 -48.7 L 9.2 -49.1 L 10.0 -50.4 L 11.4 -52.8 L 11.0 -53.1 L 14.8 -60.1 L 18.2 -69.9 L 18.6 -70.3 L 18.9 -70.3 L 19.2 -70.3 L 21.0 -69.8 L 22.6 -69.5 L 24.1 -72.5 L 30.8 -69.9 L 32.6 -69.2 L 37.2 -67.4 L 37.9 -67.3 L 38.2 -67.3 L 39.0 -67.6 L 39.4 -67.9 L 39.8 -68.4 L 40.3 -68.8 L 41.2 -71.0 L 41.6 -71.8 L 41.9 -72.6 L 42.3 -73.4 L 45.1 -72.2 L 47.3 -71.1 L 46.9 -70.4 L 46.6 -69.7 L 46.3 -69.0 L 46.2 -68.7 L 45.8 -67.8 L 45.3 -66.9 L 45.4 -66.1 L 45.1 -65.3 L 45.2 -64.7 L 45.4 -64.2 L 45.7 -63.8 L 46.0 -63.6 L 46.7 -63.2 L 51.0 -61.3 L 55.3 -59.1 L 57.5 -57.7 L 58.9 -56.7 L 59.5 -56.0 L 59.5 -55.5 L 59.4 -54.7 L 59.1 -53.7 L 58.3 -52.7 L 41.6 -35.2 L 41.3 -34.9 L 39.6 -33.1 L 37.8 -31.2 L 36.7 -30.6 L 32.3 -26.5 L 27.8 -22.8 L 27.3 -22.5 L 27.3 -22.6 L 24.1 -26.0 L 23.9 -26.3 L 25.9 -28.1 L 25.5 -28.5 Z" />
```

### Simplified Binnenalster (key shape points)

The Binnenalster can be approximated as a diamond with these 4 corners:
- **NW** (Lombardsbrücke west): SVG ~(18, -70)
- **NE** (Lombardsbrücke east / Ballindamm north): SVG ~(47, -73)
- **SE** (Ballindamm south): SVG ~(59, -55)
- **SW** (Jungfernstieg): SVG ~(8, -47) reaching to (25, -28)

### Raw Lat/Lon Coordinates (outer ring, simplified key points)

| Point | Latitude | Longitude | Description |
|-------|----------|-----------|-------------|
| SW tip | 53.5523 | 9.9946 | Southwest corner near Rathausmarkt |
| W | 53.5543 | 9.9920 | West side, Jungfernstieg |
| NW | 53.5570 | 9.9931 | Northwest, near Lombardsbrücke |
| N bridge | 53.5572 | 9.9941 | North, Lombardsbrücke connection |
| NE | 53.5573 | 9.9971 | Northeast, Kennedybrücke |
| E | 53.5567 | 9.9963 | East side, Ballindamm |
| SE | 53.5557 | 10.0000 | Southeast corner |
| S | 53.5535 | 9.9970 | South side |

---

## 2. Außenalster (Outer Alster)

**Real dimensions**: ~1,340m wide x 2,630m tall, area 1.64 km^2
**Shape**: Elongated irregular polygon, roughly pear-shaped, wider in the north, narrowing toward the south. The western shore is fairly straight (runs along Harvestehuder Weg / Alsterufer), while the eastern shore has more indentations.

### SVG Path (from OpenStreetMap relation 51218)

```svg
<path d="M 96.5 -251.1 L 99.0 -247.6 L 100.3 -246.1 L 102.4 -243.0 L 103.9 -241.5 L 104.6 -238.9 L 106.0 -235.3 L 106.6 -233.3 L 106.9 -232.2 L 107.6 -228.5 L 107.0 -225.9 L 109.0 -220.9 L 110.2 -219.4 L 112.0 -216.9 L 111.3 -214.5 L 111.6 -213.0 L 114.3 -207.9 L 116.8 -200.3 L 116.6 -197.1 L 117.7 -195.6 L 118.2 -193.8 L 119.5 -193.1 L 120.2 -193.6 L 123.4 -193.5 L 126.8 -192.9 L 130.0 -192.1 L 133.4 -190.9 L 135.2 -189.1 L 136.6 -188.3 L 138.6 -187.1 L 141.1 -185.4 L 144.5 -182.2 L 145.8 -181.1 L 147.9 -180.0 L 149.3 -178.8 L 150.8 -176.8 L 150.9 -175.0 L 151.6 -173.6 L 153.4 -171.4 L 153.8 -169.5 L 153.1 -166.4 L 153.4 -163.4 L 153.4 -161.9 L 153.5 -160.6 L 155.0 -159.1 L 154.1 -154.9 L 152.8 -150.2 L 152.0 -148.4 L 151.5 -146.7 L 151.7 -144.8 L 150.3 -138.5 L 150.3 -136.4 L 149.4 -135.5 L 147.9 -132.3 L 145.1 -128.1 L 143.8 -125.7 L 143.5 -124.3 L 142.1 -120.9 L 140.0 -117.2 L 138.5 -114.9 L 135.8 -111.6 L 135.3 -110.4 L 134.5 -109.1 L 133.4 -107.7 L 131.8 -106.4 L 130.6 -105.8 L 129.1 -105.7 L 128.2 -105.8 L 127.5 -106.8 L 126.8 -107.2 L 125.8 -107.4 L 124.4 -107.4 L 123.5 -107.1 L 122.7 -106.6 L 121.6 -105.7 L 120.7 -104.8 L 119.9 -103.9 L 119.4 -102.8 L 119.0 -101.2 L 117.3 -99.7 L 116.6 -98.7 L 115.6 -97.6 L 113.6 -96.2 L 112.4 -94.9 L 109.9 -92.7 L 107.6 -91.0 L 99.7 -86.4 L 96.3 -85.3 L 94.9 -83.6 L 92.0 -81.9 L 90.0 -82.0 L 88.8 -80.5 L 84.7 -77.9 L 82.0 -76.9 L 80.3 -76.4 L 78.5 -76.1 L 73.8 -76.0 L 71.3 -76.0 L 70.6 -76.7 L 67.6 -76.6 L 66.5 -76.5 L 66.0 -76.1 L 64.5 -75.9 L 62.6 -76.2 L 60.7 -76.6 L 57.9 -77.5 L 55.1 -78.7 L 53.5 -79.3 L 52.6 -79.4 L 51.6 -79.2 L 51.0 -78.8 L 50.5 -78.2 L 50.0 -77.4 L 49.0 -75.3 L 48.8 -74.8 L 49.0 -74.4 L 49.1 -73.8 L 49.2 -73.2 L 49.0 -72.7 L 48.8 -72.3 L 48.4 -71.8 L 48.0 -71.5 L 47.7 -71.2 L 47.3 -71.1 L 45.1 -72.2 L 42.3 -73.4 L 42.2 -73.8 L 42.1 -74.2 L 42.1 -75.1 L 42.2 -75.7 L 42.7 -76.4 L 43.3 -76.8 L 44.1 -77.0 L 45.3 -79.5 L 45.6 -80.9 L 45.5 -82.0 L 45.1 -82.9 L 44.3 -83.6 L 37.2 -86.1 L 36.1 -86.7 L 35.0 -87.9 L 34.9 -89.1 L 35.2 -90.2 L 36.0 -91.7 L 36.3 -92.4 L 36.8 -93.2 L 38.0 -93.9 L 38.3 -94.4 L 38.2 -95.0 L 38.5 -96.5 L 39.2 -98.5 L 42.1 -97.4 L 43.8 -101.6 L 41.8 -103.4 L 41.1 -104.4 L 41.2 -105.7 L 41.7 -106.9 L 44.2 -106.0 L 45.6 -109.4 L 45.1 -109.6 L 45.0 -110.2 L 44.8 -111.9 L 44.8 -113.2 L 45.0 -114.7 L 45.9 -116.9 L 46.9 -119.0 L 47.4 -120.3 L 48.1 -121.5 L 48.8 -122.5 L 49.3 -123.5 L 49.2 -123.8 L 47.8 -125.7 L 47.8 -128.1 L 48.8 -132.4 L 50.5 -138.2 L 52.5 -142.0 L 54.1 -143.9 L 55.7 -145.2 L 57.3 -146.5 L 59.0 -147.0 L 59.8 -148.1 L 61.0 -154.0 L 63.4 -158.5 L 66.3 -163.4 L 67.2 -165.8 L 68.4 -168.9 L 68.5 -171.0 L 68.1 -171.6 L 67.8 -172.5 L 68.1 -173.3 L 68.5 -174.8 L 68.6 -175.6 L 69.0 -176.6 L 69.2 -177.7 L 69.2 -178.7 L 69.2 -179.9 L 69.5 -182.6 L 70.3 -186.9 L 70.5 -187.9 L 71.8 -193.5 L 72.2 -195.5 L 72.4 -197.2 L 72.5 -200.1 L 72.5 -203.2 L 72.6 -211.0 L 74.0 -214.6 L 75.1 -216.9 L 75.4 -220.3 L 75.4 -223.3 L 75.2 -228.6 L 75.0 -236.0 L 74.8 -237.8 L 73.9 -240.7 L 73.3 -242.5 L 72.5 -244.9 L 70.5 -250.9 L 69.0 -255.3 L 67.0 -261.3 L 64.7 -267.6 L 61.1 -277.6 L 57.6 -285.6 L 55.6 -288.9 L 53.6 -291.6 L 52.0 -292.6 L 52.4 -294.6 L 54.1 -295.1 L 54.0 -296.0 L 57.5 -299.0 L 59.0 -300.8 L 59.1 -301.4 L 60.3 -301.7 L 63.9 -304.3 L 64.5 -306.1 L 65.1 -306.3 L 66.2 -306.1 L 66.6 -306.2 L 67.4 -306.2 L 68.0 -305.8 L 69.3 -305.4 L 69.8 -305.3 L 71.4 -304.3 L 72.8 -303.7 L 73.3 -303.8 L 74.1 -304.2 L 74.1 -306.7 L 74.0 -307.2 L 76.8 -306.8 L 77.3 -302.6 L 78.4 -295.3 L 79.3 -289.1 L 80.2 -282.5 L 80.8 -278.1 L 81.8 -275.3 L 82.6 -273.8 L 83.9 -272.2 L 85.3 -271.0 L 87.0 -269.9 L 89.0 -269.1 L 90.9 -268.7 L 93.2 -261.6 L 95.2 -253.1 L 95.8 -251.3 L 96.5 -251.1 Z" />
```

### Small Island in Außenalster (Alsterinsel)

```svg
<path d="M 111.8 -96.2 L 111.6 -96.4 L 111.1 -97.2 L 109.9 -97.6 L 109.0 -96.9 L 109.4 -96.2 L 109.1 -95.4 L 108.1 -95.2 L 107.7 -96.0 L 106.0 -95.1 L 104.6 -94.5 L 103.8 -96.0 L 103.4 -96.7 L 102.5 -96.2 L 99.5 -94.6 L 100.5 -92.9 L 102.0 -93.7 L 102.4 -92.9 L 102.4 -92.3 L 102.9 -91.9 L 101.4 -91.6 L 101.8 -91.2 L 102.4 -90.8 L 104.0 -91.2 L 104.7 -91.3 L 105.5 -91.8 L 106.5 -91.6 L 106.8 -92.1 L 108.0 -92.3 L 111.8 -96.2 Z" />
```

---

## 3. Hamburg Marathon 2026 Route

**Source**: Official KMZ from haspa-marathon-hamburg.de (HMH26_Marathon.kmz)
**Start/Finish**: Karolinenstraße at Hamburg Messe (lat 53.5607, lon 9.9754)
**Distance**: 42.195 km
**Character**: Flat, fast loop course

### Street-by-Street Route (in order)

1. **Karolinenstraße** (START) - at Hamburg Messe
2. **Vor dem Holstentor** / **Holstenglacis** / **Glacischaussee**
3. **Millerntorplatz** > **Reeperbahn** - Hamburg's famous entertainment district
4. **Königstraße** > **Platz der Republik**
5. **Holländische Reihe** > **Corinthstraße**
6. **Elbchaussee** - boulevard along the Elbe, views of the harbor
7. **Klopstockstraße** > **Palmaille** (in Altona)
8. Return via harbor area: **Fischmarkt**, **St. Pauli Landungsbrücken**
9. **Elbphilharmonie** / **HafenCity** / **Speicherstadt** area
10. **Wallringtunnel** (underground section)
11. **Ballindamm** - east side of Binnenalster
12. **Jungfernstieg** - south side of Binnenalster
13. **Neuer Jungfernstieg** - west side of Binnenalster
14. **Kennedybrücke** - crossing between Binnenalster and Außenalster
15. **Schwanenwik** - eastern shore of Außenalster
16. **Eduard-Rhein-Ufer** > **Schöne Aussicht** - east bank
17. **Fährhausstraße**
18. **Herbert-Weichmann-Straße** > **Sierichstraße** - northeast of Außenalster
19. **Stadtpark** - Hamburg's central park
20. **City Nord** - business district
21. **Am Hasenberge** (Ohlsdorf) - northernmost point
22. **Maienweg** - turnaround begins
23. **Alsterkrugchaussee**
24. **Rathenaustraße** > **Bebelallee**
25. **Eppendorfer Landstraße** > **Eppendorfer Baum**
26. **Klosterstern**
27. **Harvestehuder Weg** - west bank of Außenalster (elegant villas)
28. **Dammtor** - back to city center
29. **Gorch-Fock-Wall** - past Planten un Blomen park
30. **Karolinenstraße** (FINISH)

### Marathon Route KML Coordinates

The full marathon route is available as two line segments from the official 2026 KMZ file.

**Segment 1** (Start heading south through Reeperbahn, harbor, city center, then north along Außenalster to Ohlsdorf): 224 coordinate pairs

**Segment 2** (Ohlsdorf loop, return south through Eppendorf, west Alster bank, finish): 198 coordinate pairs

Raw KML data is stored in: `/Users/pietz/Private/marathon/marathon_kml/doc.kml`

### Key Marathon Waypoints (SVG coords)

| Location | SVG (x, y) | Lat, Lon |
|----------|------------|----------|
| START/FINISH (Karolinenstraße) | (-86.7, -107) | 53.5607, 9.9754 |
| Reeperbahn | (-112, -49) | 53.5549, 9.9710 |
| Elbchaussee (westernmost) | (-556, 30) | 53.5470, 9.8965 |
| Ballindamm (Binnenalster) | (60, -73) | 53.5573, 10.0010 |
| Jungfernstieg | (22, -84) | 53.5584, 9.9937 |
| Schwanenwik (east Alster) | (100, -104) | 53.5604, 10.0068 |
| Stadtpark | (152, -256) | 53.5756, 10.0155 |
| Ohlsdorf (northernmost) | (306, -728) | 53.6228, 10.0415 |
| Harvestehuder Weg | (-20, -282) | 53.5782, 9.9868 |
| Dammtor | (-7, -173) | 53.5673, 9.9889 |

---

## 4. Key Surrounding Features

### Streets Around the Alster (for map labels)

| Street | Location | SVG Position |
|--------|----------|-------------|
| **Jungfernstieg** | South side of Binnenalster, runs E-W | y ~ -30 to -48 |
| **Ballindamm** | East side of Binnenalster, runs N-S | x ~ 55 to 60 |
| **Neuer Jungfernstieg** | West side of Binnenalster | x ~ 8 to 18 |
| **Lombardsbrücke** | Bridge between the two lakes (west) | (42, -72) |
| **Kennedybrücke** | Bridge between the two lakes (east) | (45, -71) |
| **An der Alster** | East side of southern Außenalster | x ~ 100 to 120 |
| **Harvestehuder Weg** | West side of Außenalster, elegant | x ~ 38 to 50 |
| **Alsterufer** | Southwest Außenalster | x ~ 42 to 50 |
| **Schwanenwik** | Southeast Außenalster corner | (100, -100) |
| **Krugkoppelbrücke** | North entry of Außenalster (Alster river) | (68, -305) |
| **Fernsicht** | NE Außenalster | x ~ 130 to 155 |

### Landmarks

| Landmark | SVG Position | Lat, Lon |
|----------|-------------|----------|
| Hamburg Rathaus (City Hall) | (25, -20) | 53.5520, 9.9942 |
| Hotel Atlantic | (71, -85) | 53.5585, 10.0020 |
| Alsterfontäne (fountain in Binnenalster) | (36, -48) | 53.5548, 9.9961 |
| US Consulate (west Alster) | (40, -200) | 53.5700, 9.9967 |
| Elbphilharmonie | (60, 30) | 53.5470, 10.0010 |
| Hauptbahnhof (Central Station) | (85, -45) | 53.5545, 10.0043 |

---

## 5. Proportions & Layout Summary

### Relative Sizes
- **Binnenalster**: approximately 50 x 50 SVG units (small square-ish)
- **Außenalster**: approximately 120 wide x 235 tall SVG units (large elongated)
- The Außenalster is roughly **8x the area** of the Binnenalster
- They connect at SVG y ~ -71 to -73 via the Lombards/Kennedybrücke bridges

### Key Proportions
- The Binnenalster is roughly centered at SVG (35, -48)
- The Außenalster is roughly centered at SVG (89, -190)
- The gap between the two lakes (bridges) is at SVG y ~ -71
- The two lakes together span from SVG y ~ -22 (south of Binnenalster) to y ~ -307 (north of Außenalster)
- Total north-south extent: ~285 SVG units (about 3.2 km)
- Maximum east-west extent (Außenalster): ~115 SVG units (about 1.3 km)

### Orientation
- North is UP (negative Y in SVG)
- The Alster system runs roughly north-south
- The Binnenalster is slightly tilted, with its long axis running NE-SW
- The Außenalster's western shore is relatively straight, eastern shore more irregular
- The Alster river enters from the north (Krugkoppelbrücke) and exits south through the Binnenalster

---

## 6. Data Sources

- Lake polygons: OpenStreetMap (Binnenalster: relation 6693624, Außenalster: relation 51218)
- Marathon route: Official Haspa Marathon Hamburg 2026 KMZ file from mhv-maps.de
- Street information: haspa-marathon-hamburg.de official course description
- Dimensions: Wikipedia (Binnenalster, Außenalster articles)
