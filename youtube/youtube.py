from dotenv import load_dotenv
import sys,time,hashlib,os,json,re
from yt_dlp import YoutubeDL
sys.path.append('utils')
from database import insertRecord, dbQuery, hasSource
from utils import doi_from_url, pid_type
# Load environment variables from .env file
load_dotenv()


# select from db where id like 'youtu.be' or 'youtube.com'
recs = dbQuery("""SELECT identifier, uri, hash FROM harvest.vw_unique_harvest_items 
    where (identifier ilike '%%youtu.be%%' or identifier ilike '%%youtube.com%%') and doimetadata is null LIMIT 100""",(), True)

# for each record, get openaire doi's    
for rec in sorted(recs):  
    try:
        # https://www.youtube.com/watch?v=tP0iPu6fg7k
        # https://youtu.be/tP0iPu6fg7k?si=Bj32evFUTjnXCuZq

        identifier, uri, hash = rec

        playlist=False

        if 'playlist' in identifier.lower():
            url = identifier
            playlist=True
        elif '?v=' in identifier:
            vid = identifier.split('v=').pop().split('&')[0]
            url = f"https://www.youtube.com/watch?v={vid}"
        elif 'youtu.be' in identifier:
            vid = identifier.split('/').pop().split('?')[0] 
            url = f"https://www.youtube.com/watch?v={vid}"
        else:
            raise RuntimeError(f'Unrecognized youtube url format: {identifier}')

        print(f'Test {url}')

        ydl_opts = {
            "quiet": True,
            "skip_download": True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        urls = [info.get("webpage_url",url)]

        metadata = {
            "@context": "https://schema.org",
            "@type": ("VideoGallery" if playlist else "VideoObject"), 
            "@id": info.get("id",url),
            "name": info.get("title",''),
            "description": info.get("description",''),
            "creator": info.get("uploader",''),
            "channel": info.get("channel",''),
            "channel_id": info.get("channel_id",''),
            "datePublished": info.get("upload_date",''),
            "duration": info.get("duration",''),
            "view_count": info.get("view_count",''),
            "like_count": info.get("like_count",''),
            "comment_count": info.get("comment_count",''),
            "keywords": info.get("tags",''),
            "about": info.get("categories",''),
            "thumbnailUrl": info.get("thumbnail",''),
            "url": info.get("webpage_url",url),
        }
        if playlist:
            metadata["hasPart"] = [ {
                "@type": "VideoObject", 
                "@id": entry.get("id",entry.get("url")), 
                "name": entry.get("title"),
                "description": entry.get("description"),
                "url": entry.get("url")} for entry in info.get('entries', []) ]   
            

        dbQuery(f"update harvest.items set doimetadata=%s, identifiertype=%s where hash=%s",(json.dumps(metadata),'youtube',hash),False)     
    except Exception as err:
        dbQuery(f"update harvest.items set doimetadata=%s where hash=%s",(f'Failed: {err}',hash),False)     
