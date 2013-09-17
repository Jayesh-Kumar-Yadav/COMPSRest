"""
Contains the stations dictionary of valid station GET-friendly names.

Each entry in the dictionary contains the following key-value pairs:
    * collection_base - collection name
    * env - a list of valid environmental parameters in the collection
        documents.
"""


class EnvEntry(object):
    def __init__(self, collection, name='', units=''):
        self.collection = collection

        if len(name) == 0:
            col_parts = self.collection.split('-')
            self.name = col_parts[0]
            if len(units) == 0 and len(col_parts) > 1:
                self.units = col_parts[1]
            else:
                self.units = units
        else:
            self.name = name
            self.units = units


stations = {
    '1918Test': {
        'collection': '1918 Test',
        'env': [
            EnvEntry('barometric_pressure-mbars'),
            EnvEntry('wind_speed-m/s'),
            EnvEntry('sea_surface_temperature-degrees'),
            EnvEntry('wind_direction-degrees'),
            EnvEntry('relative_humidity-percent'),
            EnvEntry('air_temperature-celsius'),
            EnvEntry('buoy_compass-degrees'),
            EnvEntry('battery-volts')
        ]
    },

    '1921Test': {
        'collection': '1921 Test',
        'env': [
            EnvEntry('barometric_pressure-mbars'),
            EnvEntry('wind_speed-m/s'),
            EnvEntry('sea_surface_temperature-degrees'),
            EnvEntry('wind_direction-degrees'),
            EnvEntry('relative_humidity-percent'),
            EnvEntry('air_temperature-celsius'),
            EnvEntry('buoy_compass-degrees'),
            EnvEntry('battery-volts')
        ]
    },

    'C10MCAT': {
        'collection': 'C10 MCAT',
        'env': [
        ]
    },

    'C10': {
        'collection': 'C10',
        'env': [
        ]
    },

    'C12': {
        'collection': 'C12',
        'env': [
        ]
    },

    'FHP': {
        'collection': 'FHP',
        'env': [
            EnvEntry('water_level-m'),
            EnvEntry('wind_speed-m/s'),
            EnvEntry('water_temperature-celsius'),
            EnvEntry('number_of_outliers_wl-m'),
            EnvEntry('relative_humidity-percent'),
            EnvEntry('standard_deviation_wl-m'),
            EnvEntry('specific_conductivity-mS'),
            EnvEntry('wind_speed_sonic-m/s'),
            EnvEntry('wind_from_direction-degrees'),
            EnvEntry('wind_gust_sonic-m/s'),
            EnvEntry('air_temperature-celsius'),
            EnvEntry('precipitation-mm'),
            EnvEntry('wind_gust-m/s'),
            EnvEntry('air_pressure-mbar'),
            EnvEntry('wind_from_direction_sonic-degrees')
        ]
    }
}
