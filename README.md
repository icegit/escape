# Escape

Travel cards show a weeks-and-days countdown and a compact **5.2 kg to lose**
button, revealed using the existing right-click or two-finger tap. Hover over
that button with a mouse for 350 ms, or click/tap it, to open the weight overview.
Keyboard users can focus the revealed button and press Enter or Space.
The dialog stays open until closed with its button, Escape or the backdrop,
then returns focus to the trigger. Native `<dialog>` provides modal focus trapping.

The overview includes:

- Selected profile values: age, sex, height, latest weight, goal weight and activity factor.
- Today's Garmin-adjusted calorie allowance, activity adjustment, consumed/remaining calories and macros.
- Daily/weekly maintenance calories (TDEE), resting calories (BMR), and colour-coded BMI below weight history.
- A weight-history line chart, defaulting to 30 days, with 7/14/30/60/90-day
  views. Hover, tap or keyboard-focus a point for its date and weight. The chart
  shows the first-to-last recorded weight change in the selected period.
- Required weekly loss, daily deficit and calculated intake for the selected departure.
- Eight daily deficit scenarios: **200, 400, 600, 800, 1,000, 1,200, 1,400 and 1,600 kcal**.
  Each shows daily intake, weekly loss and projected weight at the holiday start.
- Expandable activity comparisons and three macro splits for maintenance, cutting or gaining.
- A green **Target match** marks the smallest listed deficit that reaches the
  departure goal with calculated intake at least 1,000 kcal/day. If no row
  qualifies, the table explains why; reached goals and same-day departures do
  not select a cutting row. This is a mathematical match, not a clinical recommendation.

The layout takes inspiration from [TDEECalculator.net](https://tdeecalculator.net/).
BMI categories follow the [CDC adult BMI reference](https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html).
The configured goal is separate from the BMI reference range.

## Connect Garmin

The browser never connects to Garmin. GitHub Actions reads the latest weigh-in
and profile, combines them with the target-weight secret, and refreshes
`health.json` on an Amsterdam-time schedule. It checks every 15 minutes from
06:00 through 11:45, when morning weigh-ins are most likely, then every 30
minutes for the rest of the day. A lightweight gate
converts GitHub's UTC cron candidates to `Europe/Amsterdam`, so daylight-saving
changes do not shift the local schedule. Manual workflow runs always proceed.
To support the requested overview, this file now
publishes current/goal weight, age (not birth date), sex, height, activity factor,
BMR, TDEE and measurement/calculation dates. The reveal gesture is a display
choice, not access control: this static site's JSON is publicly readable.
Credentials and the remaining Garmin profile stay out of the published data.

The sync also publishes up to 90 days of weight history, including today, as
date/kg pairs for the latest weigh-in per Garmin local calendar day. It requests
the date-range endpoint each sync, so new weigh-ins and corrections appear.
The chart uses actual calendar spacing and draws markers only for recorded
days; connecting lines do not create weigh-ins on missing days. Its vertical
axis fits the observed weights. An empty period shows an explicit empty state.
If Garmin history is temporarily unavailable, prior in-window history is
retained and the panel labels it as stale with its last successful sync date.

1. Install the pinned Garmin client:

   ```powershell
   python -m pip install -r requirements-garmin.txt
   ```

2. Create a reusable Garmin token locally, including MFA if required:

   ```powershell
   python scripts/setup_garmin_tokens.py
   ```

3. Save that token as a GitHub Actions secret:

   ```powershell
   Get-Content .garminconnect\garmin_tokens.json -Raw | gh secret set GARMIN_TOKENS_JSON
   ```

4. Push changes and run **Sync Garmin weight** from Actions.

Set `GARMIN_TARGET_WEIGHT_KG` as a repository secret. Garmin's formal Goals API
returns activity goals but does not expose the separate Weight-page target.
The target is configured privately, but the overview now publishes its value.

BMR uses the latest weight plus Garmin `userData.height` (cm), `birthDate`
and `gender`, with the [Mifflin–St Jeor equation](https://ajcn.nutrition.org/article/S0002-9165%2823%2916698-6/fulltext).
TDEE now uses average Garmin **total daily calories** (active plus resting) over
the previous 14 completed calendar days in Europe/Amsterdam. Activity factor is
that average divided by the calculated BMR; no additional exercise calories or
activity multiplier are added to Garmin's total.

The daily summaries must match the requested date, cover at least 23 hours
(allowing spring DST), include consistent finite calorie totals, and contain at
least 16 hours of measurable awake/asleep tracking. That duration is a coverage
proxy, not exact watch wear time. Zero active calories are allowed when coverage
is sufficient. Missing, incomplete and failed days are excluded from both sum
and divisor. At least 7 valid days are required. The overview reports the number
used, window end date and average active/resting/total calories; individual daily
records are not published. The successful aggregate is reused during that day's
half-hourly syncs, with the multiplier recomputed for the latest BMR. It refreshes
on the next local day; insufficient history is retried each sync.

If fewer than 7 days qualify, TDEE falls back to BMR × `GARMIN_ACTIVITY_FACTOR`
(optional secret, 1.2–2.4; default 1.2). The UI explicitly labels this as a
fallback and shows the coverage count. Garmin's activity-class number is not used.
Missing profile data keeps weight projections available and marks profile-based
metrics unavailable. Garmin calorie values remain wearable estimates.

The deficit is `kg remaining × 7,700 / calendar days remaining`. Scenario weight
is `latest weight − daily deficit × days / 7,700`. These static estimates do not
model metabolic adaptation; the [NIDDK Body Weight Planner](https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner)
provides a dynamic model. Scenario intake below 1,000 kcal/day is marked explicitly,
and a goal requiring that intake is flagged as needing more time. Scenario rows
are comparisons, not recommended calorie prescriptions. Past/today departures
never divide by zero. Macro examples are withheld below 1,000 kcal/day.

The integration uses the unofficial `garminconnect` library. If Garmin revokes
or expires the refresh token, repeat token creation and secret setup.

## Local verification

```powershell
python -m unittest discover -s scripts -p "test_*.py"
npm ci --ignore-scripts
npm test
```

DOM tests exercise the actual page loader, compact label, reveal gesture,
click/tap path, mouse-hover delay, modal contents, macro selector and closing.
They emulate native dialog opening; browser focus trapping and responsive layout
still require a browser check.
