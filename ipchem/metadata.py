

import requests

from dotenv import load_dotenv
import sys,time,hashlib,os,json
sys.path.append('utils')
from database import insertRecord, dbQuery, hasSource
# Load environment variables from .env file
load_dotenv()



label = "IPCHEM"


url="https://ipchem.jrc.ec.europa.eu/"
# add source if it does not exist
hasSource(label,url,'',label)


print('IPCHEM Publications')
headers = {'Accept': 'application/json, text/javascript, */*; q=0.01', 
           "Host": "ipchem.jrc.ec.europa.eu",
           "OWASP-CSRFTOKEN": "LFMN-B91E-RPZR-Z3UY-C3QL-N48O-SPHM-8SXG",
           "Origin": "https://ipchem.jrc.ec.europa.eu",
           "User-Agent": "Soilwise Harvest v0.1", 
           "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"}
proceed = True
client = requests.session()

# Retrieve the CSRF token first
client.get(url)  # sets cookie
if 'csrftoken' in client.cookies:
    # Django 1.6 and up
    csrftoken = client.cookies['csrftoken']
else:
    # older versions
    csrftoken = client.cookies['csrf']


records = []

myobj = {"SORT": "'Data+Collection+Acronym'+ASC",
        "PAGE_NUMBER": "1",
        "PAGE_SIZE": "50",
        "KEYWORD": "",
        "MODULE_FILTERS": "[]",
        "COUNTRIES": '',
        "CAS_NUMBER": '',
        "CHEMICAL_NAME": '',
        "MEDIA": "Soil+(Topsoil);Soil+(Subsoil)"}
resp = requests.post(url+'ipchem-data-access-p/RetrieveDataset', data=myobj, headers=headers)
print(resp.text)
resp = resp.json()
records = resp.get('Records',[])

if proceed: 
    count=len(records)
    for r in records: 
        if r.get('DATABASE'):
            myobj = {"DATASET": r.get('DATABASE')}
            resp2 = requests.post(url+'ipchem-data-access-p/GetMetadata', json=myobj, headers=headers).json()
            # {"IpchemResource": {"Module": ["Environmental Monitoring Data"], "EndDate": "2006/12/31", "Language": "", 
            # "Frequency": "irregular", "Resources": [{"Link": "http://eusoils.jrc.ec.europa.eu/ESDB_Archive/eusoils_docs/other/EUR24729.pdf", 
            # "Type": "Scientific Publication", "Title": "Evaluation of BioSoil Demonstration Project. Soil Data Analysis."}], 
            # "StartDate": "2006/01/01", "LicenceUse": [{"Link": "", "Description": "The use of the data is allowed to the European Commission Services and European Agencies only"}], 
            # "ResourceType": "chemical", "ResourceTitle": "Biosoil Data", "SpatialExtent": ["Austria", "Belgium", "Cyprus", "Czechepublic", "Germany", "Denmark", "Spain", "Estonia", "Finland", 
            # "France", "United Kingdom", "Hungary", "Ireland", "Italy", "Lithuania", "Latvia", "Portugal", "Slovakia", "Slovenia", 
            # "Sweden"], "AccessCondition": "The access is allowed to European Commission Services and European Agencies only", 
            # "ChemicalDetails": [{"CAS": "7439-96-5", "UOM": "cmol/kg", "Name": "manganese", "Media": "Soil (Topsoil)", 
            # "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7439-95-4", "UOM": "cmol/kg", "Name": "magnesium", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7439-89-6", "UOM": "mg/kg", "Name": "iron", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7439-92-1", "UOM": "mg/kg", "Name": "lead", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "63705-05-5", "UOM": "mg/kg", "Name": "sulfur", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "14452-75-6", "UOM": "mg/kg", "Name": "calcium", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7429-90-5", "UOM": "mg/kg", "Name": "aluminum", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "14452-75-6", "UOM": "cmol/kg", "Name": "calcium", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7439-95-4", "UOM": "mg/kg", "Name": "magnesium", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7440-09-7", "UOM": "mg/kg", "Name": "potassium", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7439-96-5", "UOM": "mg/kg", "Name": "manganese", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7440-09-7", "UOM": "cmol/kg", "Name": "potassium", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7440-23-5", "UOM": "cmol/kg", "Name": "sodium", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7727-37-9", "UOM": "g/kg", "Name": "nitrogen", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7440-50-8", "UOM": "mg/kg", "Name": "copper", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7440-47-3", "UOM": "mg/kg", "Name": "chromium", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7723-14-0", "UOM": "mg/kg", "Name": "phosphorus", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7440-66-6", "UOM": "mg/kg", "Name": "zinc", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7440-43-9", "UOM": "mg/kg", "Name": "cadmium", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7440-02-0", "UOM": "mg/kg", "Name": "nickel", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7440-23-5", "UOM": "mg/kg", "Name": "sodium", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7429-90-5", "UOM": "cmol/kg", "Name": "aluminum", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7439-97-6", "UOM": "mg/kg", "Name": "mercury", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}, {"CAS": "7439-89-6", "UOM": "cmol/kg", "Name": "iron", "Media": "Soil (Topsoil)", "SubstanceGroup": null, "DataCollectionName": null}], "ResourceLocator": [], "SamplingMethods": "Sampling method are  desribed into the `Manual on  methods and criteria for harmonized sampling, assessment, monitoring and analysis of the effects of air pollution on forests`, Part IIIa, Sampling and Analysis of Soil.", "AcronymShortName": "BIOSOIL", "OrganisationName": "European Commission - Joint Research Centre", "ResourceAbstract": "The BioSoil demonstration Project aimed to broaden the scope of previous forest monitoring activities (on atmospheric pollution and forest fires) to the fields of soil characteristics and biodiversity indicators. The evaluation of the project concentrated on analysing a selected number of parameters submitted by National Focal Centres (NFCs) for estimating the distribution and changes in soil organic carbon and the performance of the World Reference Base (WRB) soil classification. The spatial consistency of data reported between NFCs was found to vary significantly between sources, such as the presence of an organic layer on the over soil. The temporal stability and changes in variable parameters were assessed using data from the previous soil condition survey on Forest Focus / ICP Forests Level I sites. No clear general trend in the development of soil organic carbon over the previous survey was found, but some local changes. The results provided by the Central Laboratory suggest that some methodological differences in assessing the organic carbon content of the organic layers exist between the FSCC / ICP (International Cooperative Programme) Forests and the BioSoil survey. Those differences limit the scope of a change analysis. A particular problem in sampling and reporting data was the separation of the organic layer from the soil material, which was approached differently by the NFCs. The evaluation also concluded that the specifications provided in the Manual detailing sampling and analysis of the data collected need to be up-dated with a clear and unambiguous description of procedures to follow and making the reporting on key soil parameters a mandatory task.", "ResponsibleParty": [{"ContactName": "Diana SIMOES VIEIRA", "ContactRole": "", "EmailAddress": "Diana.SIMOES-VIEIRA@ec.europa.eu"}, {"ContactName": "Arwyn JONES", "ContactRole": "", "EmailAddress": "Arwyn.JONES@ec.europa.eu"}], "AnalyticalMethods": "", "DataAccessibility": "European Commission Services and EU Agencies", "MonitoringReasons": "The BioSoil demonstration project was one of the studies initiated in response to the stipulations of Article 6 of Regulation (EC) No. 2152/2003 (Forest Focus) to develop the monitoring scheme by means of studies, experiments, demonstration projects, testing on a pilot basis and establishment of new monitoring activities. The aim of the BioSoil project is to demonstrate how a large-scale European study can provide harmonised soil and biodiversity data and contribute to research and forest related policies. It directly supports achieving the objectives of the monitoring scheme of assessing the requirements for and develop the monitoring of soils, carbon sequestration, climate change effects and biodiversity, as well as protective functions of forests (Forest Focus, Article 1(1)b).", "OtherContributors": [], "LevelOfAggregation": "Single Measurement data"}, "General Information": {"Module": ["Environmental Monitoring Data"], "Country Coverage": ["Austria", "Belgium", "Cyprus", "Czech Republic", "Germany", "Denmark", "Spain", "Estonia", "Finland", "France", "United Kingdom", "Hungary", "Ireland", "Italy", "Lithuania", "Latvia", "Portugal", "Slovakia", "Slovenia", "Sweden"], "Granularity Level": "Single Measurement data", "Data Collection Title": "Biosoil Data", "Data Update Frequency": "irregular", "Data Collection Acronym": "BIOSOIL", "Data Collection End Date": "2006/12/31", "Data Collection Start Date": "2006/01/01"}, "Data Access & Responsibility": {"Metadata POC": {"Email": "Diana.SIMOES-VIEIRA@ec.europa.eu"}, "Data Access Level": "European Commission Services and EU Agencies", "Responsible Institution": {"Name": "European Commission - Joint Research Centre"}}, "Sampling & Analytical Information": {"Analytical Information": [{"Media": "Soil (Topsoil)", "CAS Number": "7439-96-5", "Chemical Name": "manganese", "SubstanceGroup": null, "Unit of Measure": "cmol/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7439-95-4", "Chemical Name": "magnesium", "SubstanceGroup": null, "Unit of Measure": "cmol/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7439-89-6", "Chemical Name": "iron", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7439-92-1", "Chemical Name": "lead", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "63705-05-5", "Chemical Name": "sulfur", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "14452-75-6", "Chemical Name": "calcium", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7429-90-5", "Chemical Name": "aluminum", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "14452-75-6", "Chemical Name": "calcium", "SubstanceGroup": null, "Unit of Measure": "cmol/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7439-95-4", "Chemical Name": "magnesium", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7440-09-7", "Chemical Name": "potassium", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7439-96-5", "Chemical Name": "manganese", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7440-09-7", "Chemical Name": "potassium", "SubstanceGroup": null, "Unit of Measure": "cmol/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7440-23-5", "Chemical Name": "sodium", "SubstanceGroup": nu Rll, "Unit of Measure": "cmol/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7727-37-9", "Chemical Name": "nitrogen", "SubstanceGroup": null, "Unit of Measure": "g/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7440-50-8", "Chemical Name": "copper", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7440-47-3", "Chemical Name": "chromium", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7723-14-0", "Chemical Name": "phosphorus", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7440-66-6", "Chemical Name": "zinc", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7440-43-9", "Chemical Name": "cadmium", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7440-02-0", "Chemical Name": "nickel", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7440-23-5", "Chemical Name": "sodium", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7429-90-5", "Chemical Name": "aluminum", "SubstanceGroup": null, "Unit of Measure": "cmol/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7439-97-6", "Chemical Name": "mercury", "SubstanceGroup": null, "Unit of Measure": "mg/kg", "DataCollectionName": null}, {"Media": "Soil (Topsoil)", "CAS Number": "7439-89-6", "Chemical Name": "iron", "SubstanceGroup": null, "Unit of Measure": "cmol/kg", "DataCollectionName": null}]}}


            asset = resp2.get('IpchemResource')
            if asset:
                hashcode = hashlib.md5(json.dumps(asset).encode("utf-8")).hexdigest() # get unique hash for html 
                insertRecord(   identifier='ipchem:'+ r.get('DATABASE'),
                                identifiertype='uuid',
                                title=asset.get('title',''),
                                resulttype='JSON',
                                resultobject=json.dumps(asset),
                                hashcode=hashcode,
                                source=label,
                                itemtype='dataset') # insert into db

