# Job Map Generator

This project generates an interactive map from a CSV file containing job application data. The map displays the locations of the jobs applied for, with markers indicating the status of each application.

## Prerequisites

- Python 3.x
- Required Python packages: `folium`, `requests`, `pandas`, `python-dotenv`
- A `.env` file with a Jawg maps access token

## Installation

1. Clone the repository or download the `map.py` script and the `jobs.csv` file.
2. Install the required Python packages:  
`pip install folium requests pandas python-dotenv`
3. Create a .env file in the same directory as map.py and add your Jawg Maps access token:
`ACCESS_TOKEN=your_jawg_maps_access_token`

## Usage  

1. Ensure your jobs.csv file is in the same directory as `map.py` or provide the path to the CSV file as an argument.  
2. Run the script using the following command:  
`python map.py`  
or specify a different CSV file:  
`python map.py path/to/your/jobs.csv`

## CSV File Format  

The CSV file should have the following columns:  
* `Date Applied`: The date the job application was submitted.
* `Company Name`: The name of the company.
* `Job Title`: The title of the job.
* `Location`: The location of the job (city, state).
* `Status`: The status of the application (e.g., Applied, Interview, Rejected, Withdrawn).
* `Job Posting`: The URL of the job posting.

### Example  
| Date Applied | Company Name       | Job Title                           | Location         | Status  | Job Posting                                                                 |
|--------------|--------------------|-------------------------------------|------------------|---------|-----------------------------------------------------------------------------|
| 1/29/2025    | Reliable Robotics  | Flight Software Test Environments Engineer | Mountain View, CA | Applied | [indeed.com](https://www.indeed.com/rc/clk?jk=a41cb70c5fe8811e&bb=887tvkC_rfgTrPyP2L3KGK7Jvuz-RzP1Jh45iuyE3E745QReSvAofOKZm0CoywdntGnCLto32drHgv5HKHh1nnOFJSgM2Q2RTScuFyDhWBmK7FR_DBEff48kb6eVSILa&xkcb=SoD-67M32apsOqAOob0KbzkdCdPP&fccid=a14367aef85963f7&vjs=3) |

## Output  

The script generates an HTML file (`map.html`) with an interactive map. The map includes:

* Markers for each job application location.
* Different colors for markers based on the application status:
  * Blue: Applied
  * Green: Interview
  * Red: Rejected
  * Light gray: Withdrawn/Other
* Popups and tooltips with job details and links to the job postings.

### Example  

To generate the map, run:  
`python map.py`  
This will process the `jobs.csv` file and create `map.html` in the same directory.