# AI Instructions: Add or Update Trips

Use this process whenever adding trips to `travels.json`.

## Required JSON shape

Each trip must include these keys:

```json
{
  "city": "Prague",
  "date": "2023-05-18",
  "distance": 709,
  "days": 2,
  "photo": "https://upload.wikimedia.org/...jpg",
  "hotel": "Hilton Prague Atrium",
  "address": "Pobřežní 1, Prague, Czech Republic",
  "latitude": 50.093347,
  "longitude": 14.439665,
  "checkIn": "2023-05-18",
  "checkOut": "2023-05-20"
}
```

Rules:
- Keep `travels.json` as a JSON array.
- `date`, `checkIn`, `checkOut` format: `YYYY-MM-DD`.
- `days` must equal date difference: `checkOut - checkIn`.
- `distance` is approximate km from Amsterdam (`52.3676, 4.9041`) to trip coordinates.
- For unknown hotel details on non-hotel tours, `hotel` may be `null`.

## Data sourcing rules

- Prefer completed bookings; skip canceled bookings unless explicitly requested.
- Address and coordinates should come from hotel location where possible.
- If hotel lookup fails, use city-level fallback and mark it as uncertain in the change note.
- Use attractive city photo URLs (or local files in `img/`).

## Validation checklist

1. JSON is valid.
2. All trips include required keys.
3. `distance` values are Amsterdam-based approximations.
4. `checkOut` is after `checkIn` and `days` is consistent.
5. Trips are sorted by `date` ascending.
