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
            <description>
                <![CDATA[
                    <table>
                        <thead style="border-bottom: 2px solid black;">
                            <tr>
                                <th>Parameter</th>
                                <th>Last Value</th>
                                <th>Delay (Min.)</th>
                            </tr>
                        </thead>
                        <tbody>
                            % for index, reading in enumerate(latest_readings):
                            % if index % 2 == 0:
                            <tr> 
                            % else:
                            <tr style="background: #E0E0E0;">
                            % endif
                                <td style="font-weight: bold; border-right: 1px solid black;"><span style="margin-right: 5px;">${reading[1]['parameter']}</span></td>
                                <td style="border-right: 1px solid black;">
                                    <span style="margin-left: 5px;">
                                        ${reading[1]['value']}
                                        % if reading[1]['units'] is not None:
                                        ${reading[1]['units']}
                                        % endif
                                    </span>
                                </td>
                                <td>
                                    <span style="margin-left: 5px" title="${reading[1]['timestamp'].isoformat()}Z">
                                        % if int((now - reading[1]['timestamp']).total_seconds())/60 > 240:
                                        <span style="color: red">&gt;240</span>
                                        % else:
                                        ${int((now - reading[1]['timestamp']).total_seconds())/60}
                                        % endif
                                    </span>
                                </td>
                            </tr>
                            % endfor
                        </tbody>
                    </table>
                ]]>
            </description>
            <styleUrl>#${station['type']}Style</styleUrl>
            <Point>
                <coordinates>${station['location']['coordinates'][0]},${station['location']['coordinates'][1]},0.0</coordinates>
            </Point>
        </Placemark>
    </Document>
</kml>
