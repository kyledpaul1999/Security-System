from rest_framework import viewsets, status
from rest_framework.response import Response
from recordings.models import Recording, Clip, LiveStream
from recordings.serializers import RecordingSerializer, ClipSerializer, LiveStreamStatusSerializer

class RecordingViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer

class ClipViewSet(viewsets.ModelViewSet):
    queryset = Clip.objects.all()
    serializer_class = ClipSerializer

class LiveStreamStatusViewSet(viewsets.ViewSet):
    def create(self, request):
        serializer = LiveStreamStatusSerializer(data=request.data)
        if serializer.is_valid():
            LiveStream.objects.update_or_create(
                camera=serializer.validated_data['camera'],
                defaults=serializer.validated_data
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        try:
            livestream = LiveStream.objects.get(camera_id=pk)
            livestream.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except LiveStream.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
