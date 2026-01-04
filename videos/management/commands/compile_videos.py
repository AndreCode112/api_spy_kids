from django.core.management.base import BaseCommand
from videos.Controller.Processar_video import VideoCompilerService
from videos.models import Video

class Command(BaseCommand):
    help = "Compilar Videos recolhidos, e processalos em um unico arquivo."

    def handle(self, *args, **options):
        compiler = VideoCompilerService(
            duration_limit_seconds=1800,
            hours_compilate=24
        )

        if not compiler.process_pending_videos():
            self.stderr.write(
                self.style.ERROR(f"Erro ao tentar encontrar e compilar arquivos: {compiler.strErr}")
            )
            return

        if compiler.videos_compilados:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Vídeos compilados com sucesso: {compiler.videos_compilados}"
                )
            )

            for video_id in compiler.videos_compilados:
                try:
                    video = Video.objects.get(id=video_id)
                    video.processed = True
                    video.save()
                except Video.DoesNotExist:
                    self.stderr.write(
                        self.style.ERROR(f"Vídeo com ID {video_id} não encontrado para marcar como processado.")
                    )


        else:
            self.stdout.write(
                self.style.WARNING("Nenhum vídeo foi encontrado para compilação.")
            )
