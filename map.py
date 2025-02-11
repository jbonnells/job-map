import os, folium, requests, argparse
import pandas as pd
from folium import Popup
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

def get_coordinates(address):
    url = f"https://nominatim.openstreetmap.org/search"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0'}
    
    params = {
        'q': address,
        'format': 'json'
    }
    
    response = requests.get(url, params=params, headers=headers)
    
    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        return None

    if not response.content:
        print("Error: Empty response")
        return None
    
    if 'application/json' not in response.headers.get('Content-Type', ''):
        print("Error: Response is not in JSON format")
        print("Response content:", response.content)
        return None
    
    try:
        data = response.json()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    
    except Exception as ex:
        print(ex)

def run(df, map_filename='map.html'):
    us_center = [39.8283, -115.5795]  # Center of the western half of the U.S.
    my_map = folium.Map(location=us_center, zoom_start=5)
    folium.TileLayer(
        tiles=f'https://tile.jawg.io/jawg-dark/{{z}}/{{x}}/{{y}}{{r}}.png?access-token={ACCESS_TOKEN}',  # URL template for the custom tiles
        attr='<a href="https://jawg.io" title="Tiles Courtesy of Jawg Maps" target="_blank">&copy; <b>Jawg</b>Maps</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',  # Custom attribution
        name='Jawg_Dark',
        min_zoom=0,
        max_zoom=22,
    ).add_to(my_map)
    map_data = {}
    
    dates_applied = df['Date Applied'].tolist()
    company_names = df['Company Name'].tolist()
    job_titles = df['Job Title'].tolist()
    addresses = df['Location'].tolist()
    job_status = df['Status'].tolist()
    job_postings = df['Job Posting'].tolist()
    zipped = zip(dates_applied,company_names,job_titles,addresses,job_postings,job_status)
    iter_count = 1
    pending_jobs = []

    for date,name,title,address,link,status in zipped:
        print(f'Processing ({iter_count}/{df.shape[0]}): {title}, {name}, {address}')
        try:
            date = str(date).split(' ')[0] # remove time
            text = f'{name} - {title} - {status} - {date}'
            color = 'blue' if 'Applied' in status else 'green' if 'Interview' in status else 'red' if 'Rejected' in status else 'lightgray'
            coords = get_coordinates(address)

            if coords is None:
                print(f"Error: Unable to get coordinates for {address}")
                continue

            if coords not in map_data.keys():
                map_data[coords] = []

            map_data[coords].append({
                'date': date,
                'address': address,
                'text': text,
                'color': color,
                'link': link
            })

            job_info = {
                'date': str(date).split(' ')[0],
                'text': f'{name} - {title}',
                'color': color,
                'link': link,
                'coords': coords
            }
            if color in ['blue', 'green']:
                pending_jobs.append(job_info)
            
        except Exception as ex:
            print(ex)

        iter_count += 1

    for coords,params in map_data.items():
        text = ''
        for v in params:
            text += f"<a href=\"{v['link']}\" target=\"_blank\">{v['text']}</a><br>"
            color = v['color']

        folium.CircleMarker(
                popup=Popup(text, max_width=500),
                tooltip=text,
                location=coords,
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85
            ).add_to(my_map)

    # Add a legend to the map
    legend_html = '''
        <div style="position: fixed; 
        bottom: 50px; right: 10px; width: 150px; height: 150px; 
        border:2px solid grey; z-index:9999; font-size:14px;
        background-color:#2A2B2B; opacity: 0.8; color: white;">
        &nbsp; <b>Legend</b> <br>
        &nbsp; <i class="fa fa-circle" style="color:blue"></i>&nbsp; Applied <br>
        &nbsp; <i class="fa fa-circle" style="color:green"></i>&nbsp; Interview Pending <br>
        &nbsp; <i class="fa fa-circle" style="color:red"></i>&nbsp; Rejected <br>
        &nbsp; <i class="fa fa-circle" style="color:lightgray"></i>&nbsp; Withdrawn/Other <br>
        </div>
        '''
    my_map.get_root().html.add_child(folium.Element(legend_html))

    list_items_html = ""
    for job in pending_jobs:
        lat, lng = job['coords']
        list_items_html += (
            f'<div onclick="centerMap({lat}, {lng})" style="cursor:pointer; margin-bottom:5px;">'
            f'<i class="fa fa-circle" style="color:{job["color"]}"></i> {job["text"]}'
            '</div>'
        )
    list_html = f'''
    <div style="position: fixed; top: 10px; right: 10px; width: 400px; border:2px solid grey; z-index:9999; font-size:14px;
        background-color:#2A2B2B; opacity: 0.8; color: white;">
        <div id="listHeader" style="padding: 10px; cursor: pointer;" onclick="toggleList()">Pending Jobs &#9654;</div>
        <div id="jobList" style="height:300px; overflow-y:auto; padding:10px; display:none;">
            {list_items_html}
        </div>
    </div>
    '''
    my_map.get_root().html.add_child(folium.Element(list_html))

    center_script = f"""
    <script>
    function toggleList() {{
        var list = document.getElementById('jobList');
        var header = document.getElementById('listHeader');
        if(list.style.display === 'none') {{
            list.style.display = 'block';
            header.innerHTML = 'Pending Jobs &#9660;';
        }} else {{
            list.style.display = 'none';
            header.innerHTML = 'Pending Jobs &#9654;';
        }}
    }}
    function centerMap(lat, lng) {{
        {my_map.get_name()}.setView([lat, lng], 12);
    }}
    </script>
    """
    my_map.get_root().html.add_child(folium.Element(center_script))

    my_map.save(map_filename)
    print(f"Map saved as {map_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a map from an CSV file of job postings and locations.')
    parser.add_argument('file_path', type=str, nargs='?', help='Path to the CSV file', default="./jobs.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.file_path)
    run(df)