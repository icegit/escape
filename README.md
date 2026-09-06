# Escape

Travel cards show a weeks-and-days countdown and a compact **5.2 kg to lose**
button, revealed using the existing right-click or two-finger tap. Hover over
that button with a mouse for 350 ms, or click/tap it, to open the weight overview.
Keyboard users can focus the revealed button and press Enter or Space.
The dialog stays open until closed with its button, Escape or the backdrop,
then returns focus to the trigger. Native `<dialog>` provides modal focus trapping.

The overview includes:

- Selected profile values: age, sex, height, latest weight, goal weight and activity factor.
- Daily/weekly maintenance calories (TDEE), resting calories (BMR), BMI and reference range.
- Required weekly loss, daily deficit and calculated intake for the selected departure.
- Eight daily deficit scenarios: **200, 400, 600, 800, 1,000, 1,200, 1,400 and 1,600 kcal**.
  Each shows daily intake, weekly loss and projected weight at the holiday start.
- Expandable activity comparisons and three macro splits for maintenance, cutting or gaining.

The layout takes inspiration from [TDEECalculator.net](https://tdeecalculator.net/).
BMI categories follow the [CDC adult BMI reference](https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html).
The configured goal is separate from the BMI reference range.

## Connect Garmin

The browser never connects to Garmin. GitHub Actions reads the latest weigh-in
and profile, combines them with the target-weight secret, and refreshes
`health.json` every 30 minutes. To support the requested overview, this file now
publishes current/goal weight, age (not birth date), sex, height, activity factor,
BMR, TDEE and measurement/calculation dates. The reveal gesture is a display
choice, not access control: this static site's JSON is publicly readable.
Credentials and the remaining Garmin profile stay out of the published data.

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

TDEE uses the latest weight plus Garmin `userData.height` (cm), `birthDate`
and `gender`, with the [Mifflin–St Jeor equation](https://ajcn.nutrition.org/article/S0002-9165%2823%2916698-6/fulltext).
Set the optional `GARMIN_ACTIVITY_FACTOR` Actions secret to an activity multiplier
(1.2–2.4). The default is a sedentary assumption of 1.2, displayed in the overview.
Garmin's activity-class number is not treated as a TDEE multiplier. Missing
profile data keeps weight projections available and marks profile-based metrics
unavailable. The loader retains all validated overview fields, including TDEE.

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
