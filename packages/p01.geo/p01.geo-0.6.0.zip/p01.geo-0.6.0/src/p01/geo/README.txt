======
README
======

This package provides a geo locaiton database supporting longitude/latitude,
country, city and timezone lookup based on the MaxMind geo location database.

  >>> import os.path
  >>> import p01.geo.locator

  >>> path = os.path.join(os.path.dirname(p01.geo.__file__), 'data')
  >>> db = os.path.join(path, 'GeoLiteCity.dat')
  >>> tzdb = os.path.join(path, 'time_zone.csv')
  >>> locator = p01.geo.locator.GeoLocator(db, tzdb)
  >>> locator
  <p01.geo.locator.GeoLocator object at ...>


The locator provides a generic API where we can get all data based on a given
IP adress:

  >>> ip = '86.101.28.131'
  >>> data = locator.getData(ip)
  >>> data
  <GeoData for 86.101.28.131>

  >>> data.countryCode
  'HU'

  >>> data.countryCode3
  'HUN'

  >>> data.countryName
  'Hungary'

  >>> data.regionName is None
  True

  >>> data.metroCode is None
  True

  >>> data.city
  u'Budapest'

  >>> data.timezone
  <DstTzInfo 'Europe/Budapest' CET+1:00:00 STD>

  >>> data.longitude
  19.0833...

  >>> data.latitude
  47.5

  >>> data.postalCode is None
  True

Looking up a timezone based on IP is faster and consumes less RAM for caching:

  >>> tz = locator.getTimeZone(ip)
  >>> tz
  <DstTzInfo 'Europe/Budapest' CET+1:00:00 STD>

As you can see the teimzone can we get with the zone property (non unicode):

  >>> tz.zone
  'Europe/Budapest'

Not all IPs are present:

  >>> ip = '162.220.213.213'
  >>> locator.getData(ip) is None
  True

  >>> locator.getTimeZone(ip) is None
  True

We get exceptions on bad IPs:

  >>> ip = '86.101.28.13x'
  >>> locator.getData(ip) is None
  True

  >>> locator.getTimeZone(ip) is None
  True

We can get a locator that loads the db and tzdb and stays around
in a global variable:

  >>> from p01.geo.locator import get_loaded_locator
  >>> locator = get_loaded_locator()

This locator will work just like normal

  >>> ip = '217.10.9.34'
  >>> locator.getData(ip)
  <GeoData for 217.10.9.34>

Running get_loaded_locator will get us the same locator again,
there is no fresh delay to load the db and tzdb:

  >>> locator2 = get_loaded_locator()
  >>> locator is locator2
  True

We can override the paths for the db and tzdb when loading the locator:

  >>> path = os.path.join(os.path.dirname(p01.geo.__file__), 'data')
  >>> db = os.path.join(path, 'GeoLiteCity.dat')
  >>> tzdb = os.path.join(path, 'timezone.txt')
  >>> paths = {'db':db, 'tzdb':tzdb}
  >>> locator = get_loaded_locator(paths)
  >>> locator
  <p01.geo.locator.GeoLocator object at ...>
