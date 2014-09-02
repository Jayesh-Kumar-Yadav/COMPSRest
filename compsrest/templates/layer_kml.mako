<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
    <Document>
        <Style id="buoyStyle">
            <IconStyle>
                <Icon>
                    <href>${request.static_url('compsrest:static/img/secoora-buoy-default.png')}</href>
                </Icon>
            </IconStyle>
        </Style>
        <Style id="coastalStyle">
            <IconStyle>
                <Icon>
                    <href>${request.static_url('compsrest:static/img/secoora-shore_station-default.png')}</href>
                </Icon>
            </IconStyle>
        </Style>
        <Placemark id="${station['uri']}">
            <name>${station['name']}</name>
            <styleUrl>#${station['type']}Style</styleUrl>
            <Point>
                <coordinates>${station['location']['coordinates'][0]},${station['location']['coordinates'][1]},0.0</coordinates>
            </Point>
        </Placemark>
    </Document>
</kml>
