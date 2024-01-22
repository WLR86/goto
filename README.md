To get the right ascension (RA) and declination (Dec) coordinates of Mars from a given position on Earth using Python and Skyfield, you can follow these steps:

1. Install the necessary packages:
   ```
   pip install skyfield
   ```

2. Import the required modules:
   ```python
   from skyfield.api import Topos, load
   from datetime import datetime
   ```

3. Load the necessary data files:
   ```python
   planets = load('de421.bsp')
   earth = planets['earth']
   mars = planets['mars']
   ```

4. Define the observer's location on Earth:
   ```python
   observer_latitude = 51.5074  # Example latitude (London)
   observer_longitude = -0.1278  # Example longitude (London)
   observer_location = earth.topos(observer_latitude, observer_longitude)
   ```

5. Get the current time:
   ```python
   current_time = datetime.utcnow()
   ```

6. Calculate the position of Mars relative to the observer:
   ```python
   astrometric = observer_location.at(current_time).observe(mars)
   apparent = astrometric.apparent()
   ra, dec, distance = apparent.radec()
   ```

7. Print the RA and Dec coordinates of Mars:
   ```python
   print(f"RA: {ra.hours:02.0f}h {ra.minutes:02.0f}m {ra.seconds:02.0f}s")
   print(f"Dec: {dec.degrees:02.0f}° {dec.minutes:02.0f}' {dec.seconds:02.0f}\"")
   ```

Make sure you have the `de421.bsp` data file in the same directory as your Python script. This file contains the necessary planetary ephemeris data for accurate calculations.

Note: The example latitude and longitude used in this code are for London. Replace them with the desired observer's latitude and longitude.

# Other resources
https://lguerriero.opendatasoft.com/

Messier catalog
https://lguerriero.opendatasoft.com/api/explore/v2.1/catalog/datasets/catalogue-de-messier/records?select=messier%2Cngc%2Cra%2Cdec&limit=110

# the API limits number of records so it's easier to get the whole thing instead
https://lguerriero.opendatasoft.com/api/explore/v2.1/catalog/datasets/ngc-ic-messier-catalog/exports/json?lang=en&timezone=Europe%2FBerlin
