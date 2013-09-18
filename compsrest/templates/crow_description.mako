% if 'description' in station:
<p>${station['description']}</p>
% endif

<table class="table">
    <tbody>
        <tr>
            <th>Owner</th>
            <td>${station['owner']}</td>
        </tr>
        <tr>
            <th>Type</th>
            <td>${station['station_type']}</td>
        </tr>
    </tbody>
</table>
