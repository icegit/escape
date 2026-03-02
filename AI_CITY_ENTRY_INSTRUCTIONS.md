# AI Instructions: Trip/Stay JSON Rules

Use this process whenever editing `travels.json`.

## JSON structure

Top-level array contains trip objects.  
Each trip contains a `stays` array.

```json
{
  "city": "Bouillon + 2 more",
  "date": "2017-08-19",
  "distance": 286,
  "days": 3,
  "photo": "bouillon.webp",
  "stays": [
    {
      "hotel": "Auberge de Jeunesse de Bouillon",
      "address": "Route du Christ 16, 6830 Bouillon, Belgium",
      "latitude": 49.793426,
      "longitude": 5.07283,
      "checkIn": "2017-08-19",
      "checkOut": "2017-08-20"
    }
  ]
}
```

## Grouping rule

- Group stays into the same trip when `next.checkIn <= previous.checkOut + 3 days`.
- Start a new trip only when the gap is more than 3 days.

## Field ownership

- Trip object keeps: `city`, `date`, `distance`, `days`, `photo`, `stays`.
- Trip object must NOT keep: `hotel`, `address`, `latitude`, `longitude`, `checkIn`, `checkOut`.
- Stay object keeps: `hotel`, `address`, `latitude`, `longitude`, `checkIn`, `checkOut`.
- Stay object must NOT keep: `city`, `date`, `distance`, `days`, `photo`.

## Image rules

- Store all trip photos in local `img/` folder.
- Use realistic, vibrant travel photos only (no SVG, map, icon, or illustration).
- Convert and save all trip photos as `.webp`.
- Max image width is `1024px`.
- `photo` must reference the local `.webp` filename.

## Validation checklist

1. JSON is valid.
2. Trips are sorted by `date` ascending.
3. Every trip has a non-empty `stays` array.
4. `days` equals `trip_end - trip_start`.
5. Every stay has valid `checkIn/checkOut` and no forbidden keys.
6. All `photo` files exist under `img/` and are WebP with width <= 1024.
