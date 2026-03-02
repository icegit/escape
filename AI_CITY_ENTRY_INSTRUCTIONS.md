# AI Instructions: Add a New Destination

Use this process whenever adding a new destination to `travels.json`.

## Required JSON format

Each item must contain exactly these 5 keys, in this order:

```json
{
  "city": "Mexico Tour",
  "date": "2022-01-16",
  "distance": 3310,
  "days": 9,
  "photo": "yucatan.jpg"
},
```

Rules:
- Keep `travels.json` as a JSON array.
- No extra keys (no hotel, address, phone, etc.).
- `date` format: `YYYY-MM-DD`.
- `distance`: integer kilometers from Amsterdam.
- `photo`: lowercase one-word filename where possible, e.g. `paris.jpg`, `hamburg.jpg`.

## Distance rule (Amsterdam baseline)

Calculate approximate great-circle distance from Amsterdam (`52.3676, 4.9041`) to the destination anchor:
- If `city` is a city name, use that city center.
- If it is a tour/cruise, use a clear primary anchor city (example: `Mexico Tour` -> Cancun).
- Round to nearest kilometer.

## Photo rule

- Save the image in `img/`.
- Prefer attractive landscape photos.
- Use one-word, lowercase filename where possible.
- Update `photo` in `travels.json` to match the file name.

## Validation checklist

1. JSON is valid.
2. Every item has only `city`, `date`, `distance`, `days`, `photo`.
3. Distance is an Amsterdam-based approximation.
4. Photo file exists in `img/`.
5. Page renders correctly in `index.html`.
