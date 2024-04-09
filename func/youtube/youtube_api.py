from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import pickle

def authenticate():
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    # Cargar credenciales desde un archivo pickle si existe
    if os.path.exists("func/youtube/youtube_token.pickle"):
        with open("func/youtube/youtube_token.pickle", "rb") as token:
            creds = pickle.load(token)
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "func/youtube/credentials.json", scopes=scopes
        )
        creds = flow.run_local_server(port=0)

        # Guardar las credenciales en un archivo pickle para futuras ejecuciones
        with open("func/youtube/youtube_token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

def get_latest_videos(youtube, channel_id):
    videos_data = []
    # Realizar la solicitud para obtener los últimos videos del canal
    request = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        order="date",
        type="video",
    )
    response = request.execute()

    # Imprimir los títulos de los últimos videos
    for item in response["items"]:
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]
        description = item["snippet"]["description"]
        thumbnails = item["snippet"]["thumbnails"]
        published_at = item["snippet"]["publishedAt"]

        # Obtener más detalles del video
        video_details = youtube.videos().list(
            part="contentDetails",
            id=video_id
        ).execute()
        content_details = video_details["items"][0]["contentDetails"]

        # Crear un diccionario con los datos del video
        video_data = {
            "IDVideo": video_id,
            "Title": title,
            "Description": description,
            "Thumbnails": thumbnails,
            "Published At": published_at,
            "Content Details": content_details
        }

        # Agregar el diccionario a la lista
        videos_data.append(video_data)

    videos_data.reverse()

    return videos_data
