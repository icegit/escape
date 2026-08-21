# Escape

The travel cards default to a weeks-and-days countdown. A private Garmin Connect
sync can add a weight-goal line below it, such as `2.5 kg to lose`.

## Connect Garmin

The browser never connects to Garmin and the repository never publishes exact
weights. GitHub Actions reads the latest weigh-in and active weight goal, then
writes only their difference to `health.json` every 30 minutes.

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

If Garmin Connect has no active weight goal, set `GARMIN_TARGET_WEIGHT_KG` as a
repository secret. This fallback is optional; normally the target is read from
Garmin.

The integration uses the unofficial `garminconnect` library because Garmin's
official Health API is limited to approved business integrations. If Garmin
revokes or expires the refresh token, repeat steps 2 and 3.

## Local verification

```powershell
python -m unittest discover -s scripts -p "test_*.py"
```
