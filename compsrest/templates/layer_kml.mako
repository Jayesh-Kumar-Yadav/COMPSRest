<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document>
        <Placemark id="${station['uri']}">
            <name>${station['name']}</name>
            <Point>
                <coordinates>${station['location']['coordinates'][0]},${station['location']['coordinates'][1]},0.0</coordinates>
            </Point>
        </Placemark>
    </Document>
</kml>