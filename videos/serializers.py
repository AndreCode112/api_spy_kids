# videos/serializers.py
from rest_framework import serializers
from .models import Video, VideoGroup
from datetime import timedelta


class VideoSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Video
        fields = ['id', 'file', 'created_at', 'duration', 'duration_seconds', 'video_group', 'processed']
        read_only_fields = ['id', 'duration', 'video_group', 'processed']
    
    def create(self, validated_data):
        duration_seconds = validated_data.pop('duration_seconds')
        validated_data['duration'] = timedelta(seconds=duration_seconds)
        return super().create(validated_data)


class VideoGroupSerializer(serializers.ModelSerializer):
    videos = VideoSerializer(many=True, read_only=True)
    video_count = serializers.SerializerMethodField()
    remaining_duration_seconds = serializers.SerializerMethodField()
    is_full = serializers.SerializerMethodField()
    
    class Meta:
        model = VideoGroup
        fields = ['id', 'created_at', 'start_time', 'end_time', 'total_duration', 
                  'consolidated_path', 'videos', 'video_count', 'remaining_duration_seconds', 'is_full']
    
    def get_video_count(self, obj):
        return obj.videos.count()
    
    def get_remaining_duration_seconds(self, obj):
        """Retorna quantos segundos ainda podem ser adicionados ao grupo"""
        return obj.get_remaining_duration().total_seconds()
    
    def get_is_full(self, obj):
        """Indica se o grupo já atingiu o limite de 20 minutos"""
        return obj.get_remaining_duration().total_seconds() <= 0