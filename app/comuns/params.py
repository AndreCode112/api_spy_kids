import os

class Tparams:
    API_BASE_URL ="https://spykids.pythonanywhere.com"
    API_BASE_URL_SERVER_UPLOAD ="https://rcamgeo.com.br"
    UPLOAD_URL = f"{API_BASE_URL}/api/video/upload/"
    UPLOAD_EXTERNALSERVER_URL = f"{API_BASE_URL_SERVER_UPLOAD}/api/api_upload_arquivos.php"
    APICONFIGDEVICEAUDIO_URL = f"{API_BASE_URL}/api/config/device/audio/" 
    APIGETCONFIGDEVICE_URL = f"{API_BASE_URL}/api/config/device/"
    APIINSERTLOGONSERVER = f"{API_BASE_URL}/api/logs/"



    AppData =  os.getenv('APPDATA')
    pathFileLogs =  AppData + "\\logsSpyKids\\LogsApiSpyKids.txt"


    CONNECTIONINFO_URL = f"{API_BASE_URL}/api/devices/status/"

    videoUploadPathName = "records_spy_kids"
    thubnailUploadPathName = "thumbnails_spy_kids"


    if not os.path.exists(videoUploadPathName):
        os.makedirs(videoUploadPathName)

    if not os.path.exists(thubnailUploadPathName):
        os.makedirs(thubnailUploadPathName)

    VIDEO_FILENAME = "video.temp.mp4"

    pathVideoUploadSave = videoUploadPathName + "/" + VIDEO_FILENAME



    audio:str =''
    duration_capture:int

