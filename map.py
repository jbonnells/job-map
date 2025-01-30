import os, folium, requests, argparse
import pandas as pd
from folium import Popup
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv('ACCESS_TOKEN')

def get_coordinates(city=None, state=None, name=None):
    url = f"https://nominatim.openstreetmap.org/search"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) Gecko/20100101 Firefox/134.0'}
    
    if name is not None:
        params = {
            'q': f'{name},{city},{state}',
            'format': 'json'
        }
    else:
        params = {
            "city": city,
            "state": state,
            "country": "USA",
            "format": "json"
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
        else:
            return get_coordinates(city, state)
    
    except Exception as ex:
        print(ex)

def run(df, map_filename='map.html'):
    us_center = [39.8283, -115.5795]  # Center of the western half of the U.S.
    my_map = folium.Map(location=us_center, zoom_start=6)
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
    locations = df['Location'].tolist()
    job_status = df['Status'].tolist()
    job_postings = df['Job Posting'].tolist()
    zipped = zip(dates_applied,company_names,job_titles,locations,job_postings,job_status)
    iter_count = 1

    for date,name,title,location,link,status in zipped:
        print(f'Processing ({iter_count}/{df.shape[0]}): {title}, {name}, {location}')
        try:
            date = str(date).split(' ')[0] # remove time
            city = location.split(',')[0].strip()
            state = location.split(',')[1].strip()
            coords = get_coordinates(city, state, name)
            size = locations.count(location) + 1
            text = f'{name} - {title} - {status} - {date}'
            color = 'blue' if status == 'Applied' else 'green' if status == 'Interview' else 'red' if status == 'Rejected' else 'lightgray'

            if coords not in map_data.keys():
                map_data[coords] = []

            map_data[coords].append({
                'date': date,
                'city': city,
                'state': state,
                'size': size,
                'text': text,
                'color': color,
                'link': link
            })
            
        except Exception as ex:
            print(ex)

        iter_count += 1

    for coords,params in map_data.items():
        text = ''
        for v in params:
            text += f"<a href=\"{v['link']}\" target=\"_blank\">{v['text']}</a><br>"
            radius = v['size']
            color = v['color']

        folium.CircleMarker(
                popup=Popup(text, max_width=500),
                tooltip=text,
                location=coords,
                radius=radius,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.85
            ).add_to(my_map)

    # Add a legend to the map
    legend_html = '''
        <div style="position: fixed; 
        bottom: 50px; left: 50px; width: 150px; height: 150px; 
        border:2px solid grey; z-index:9999; font-size:14px;
        background-color:#2A2B2B; opacity: 0.8; color: white;">
        &nbsp; <b>Legend</b> <br>
        &nbsp; <i class="fa fa-circle" style="color:blue"></i>&nbsp; Applied <br>
        &nbsp; <i class="fa fa-circle" style="color:green"></i>&nbsp; Interview <br>
        &nbsp; <i class="fa fa-circle" style="color:red"></i>&nbsp; Rejected <br>
        &nbsp; <i class="fa fa-circle" style="color:lightgray"></i>&nbsp; Withdrawn/Other <br>
        </div>
        '''
    my_map.get_root().html.add_child(folium.Element(legend_html))

    my_map.save(map_filename)
    print(f"Map saved as {map_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate a map from an Excel file of locations.')
    parser.add_argument('file_path', type=str, nargs='?', help='Path to the Excel file containing locations', default="./jobs.xlsx")
    args = parser.parse_args()

    df = pd.read_excel(args.file_path)
    run(df)