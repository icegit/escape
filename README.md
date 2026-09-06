# Escape

The travel cards default to a weeks-and-days countdown. A private Garmin Connect
sync adds a weight plan below it, revealed using the existing right-click or
two-finger tap. For example:

```text
4.3 kg to lose (−0.9 kg/week · ≈974 kcal/day deficit)
Estimated TDEE 2,400 kcal/day · activity factor 1.2
Estimated intake ≈1,426 kcal/day
```

Weekly loss and daily deficit use the remaining calendar days until each trip.
The goal remains your configured target weight; TDEE does not determine an
ideal weight. Departures today and reached goals do not calculate a loss rate.

## Connect Garmin

The browser never connects to Garmin and the repository never publishes exact
weights. GitHub Actions reads the latest weigh-in from Garmin, combines it with
the private target-weight secret, then writes their difference and estimated TDEE to
`health.json` every 30 minutes.

1. Install the pinned Garmin client:

   ```powershell
   python -m pip install -r requirements-garmin.txt
   ```

2. Create a reusable Garmin token locally. This step supports Garmin MFA:

   ```powershell
   python scripts/setup_garmin_tokens.py
   ```

3. Save that token as a GitHub Actions secret:

   ```powershell
   Get-Content .garminconnect\garmin_tokens.json -Raw | gh secret set GARMIN_TOKENS_JSON
   ```

4. Push the changes, then run **Sync Garmin weight** once from the repository's
   Actions tab. Scheduled refreshes will run automatically afterward.

Set `GARMIN_TARGET_WEIGHT_KG` as a repository secret. Garmin's formal Goals API
returns activity goals but does not expose the separate target shown on the
Weight page, and its older wellness-goal endpoint is no longer available.
Keeping the target in a secret also prevents it from being published.

TDEE uses the latest weight plus Garmin `userData.height` (cm), `birthDate`
and `gender`, with the [Mifflin–St Jeor equation](https://ajcn.nutrition.org/article/S0002-9165%2823%2916698-6/fulltext).
Only the resulting TDEE and activity factor are published, not the profile.
Set the optional `GARMIN_ACTIVITY_FACTOR` Actions secret to your activity
multiplier (1.2–2.4). The default is an explicit sedentary assumption of 1.2;
Garmin's activity-class number is not treated as a TDEE multiplier.
Missing or invalid profile data leaves the weight/deficit display available
and labels TDEE unavailable. The new TDEE field appears after the next successful
sync with the updated code.

The deficit is an approximate `kg remaining × 7,700 / days remaining`, and
estimated intake is TDEE minus that deficit. This is a static estimate, not a
prediction of metabolic adaptation. The [NIDDK Body Weight Planner](https://www.niddk.nih.gov/health-information/weight-management/body-weight-planner)
provides a dynamic model. Calculated intake below 1,000 kcal/day is replaced with
a message to allow more time, consistent with the planner's minimum intake guard.

The integration uses the unofficial `garminconnect` library because Garmin's
official Health API is limited to approved business integrations. If Garmin
revokes or expires the refresh token, repeat steps 2 and 3.

## Local verification

```powershell
python -m unittest discover -s scripts -p "test_*.py"
node --test scripts/test_weight_plan.cjs
```
