import os
import tempfile
from datetime import timedelta
from django.utils import timezone
from django.core.files import File
from moviepy import VideoFileClip, concatenate_videoclips
from videos.models import Video, CompiledVideo

class VideoCompilerService:
    def __init__(self, duration_limit_seconds:int, hours_compilate:int):
        self.max_duration_seconds:int = duration_limit_seconds
        self.hours_compilate:int = hours_compilate

        self.strErr: str = ''
        self.videos_compilados:list = []

    def process_pending_videos(self) -> bool:
        now = timezone.now()
        time_threshold = now - timedelta(hours=self.hours_compilate)

        try: 
            videos_qs = Video.objects.filter(
                processed=False,
                created_at__gte=time_threshold
            ).order_by('created_at')

            if not videos_qs.exists():
                self.videos_compilados = []
                return True

            
            Lista_videos_para_processar:list = []
            variavel_duração_video_processar:float = 0.0

            for video in videos_qs:
                vid_duration = video.duration.total_seconds() if video.duration else 0
                variavel_duração_video_processar += vid_duration

                if variavel_duração_video_processar > self.max_duration_seconds:
                    
                    if Lista_videos_para_processar:
                        if not self._create_video_file(Lista_videos_para_processar):
                            return False
                       
                    
                    Lista_videos_para_processar = [video]
                    self.videos_compilados.append(video.id)
                    
            return True
        
        except Exception as e:
            self.strErr = f"Erro ao processar vídeos: {e}"
            return False

    def _create_video_file(self, videos):
        clips = []
        temp_filename = None
        final_clip = None

        try:
            for v in videos:
                if os.path.exists(v.file.path):
                    clip = VideoFileClip(v.file.path)
                    clips.append(clip)
                
            if not clips:
                return False

            final_clip = concatenate_videoclips(clips, method="compose")

            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                temp_filename = temp_file.name

            final_clip.write_videofile(
                temp_filename, 
                codec='libx264', 
                audio_codec='aac', 
                preset='ultrafast', 
                threads=4,
                logger=None
            )

            compiled_obj = CompiledVideo()
            
            with open(temp_filename, 'rb') as f:
                name = f'compilado_{timezone.now().timestamp()}.mp4'
                compiled_obj.file.save(name, File(f), save=False)
                
                total_dur = sum(v.duration.total_seconds() for v in videos if v.duration)
                compiled_obj.total_duration = timedelta(seconds=total_dur)
                compiled_obj.save()
                
                compiled_obj.source_videos.set(videos)

            for v in videos:
                v.processed = True
                v.save()


            return True
        
        except Exception as e:
            self.strErr = f"Erro ao compilar vídeos: {e}"
            return False
            
        finally:
            for clip in clips:
                try: clip.close()
                except: pass
            
            if final_clip:
                try: final_clip.close()
                except: pass

            if temp_filename and os.path.exists(temp_filename):
                try: os.remove(temp_filename)
                except OSError: pass