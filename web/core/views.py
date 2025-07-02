from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Agent, Command, Metric
from .serializers import HeartbeatSerializer, CommandResultSerializer

# Récupère le CN du certificat client (passé par Nginx)

def _agent_from_cert(request):
    return request.META.get('HTTP_X_SSL_CLIENT_S_DN_CN') or request.headers.get('X-Agent-UUID')

class Heartbeat(APIView):
    def post(self, request):
        data = HeartbeatSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        agent_uuid = _agent_from_cert(request)
        print(agent_uuid)
        agent, _ = Agent.objects.get_or_create(uuid=agent_uuid,
                                               defaults={'hostname': data.validated_data['hostname'],
                                                         'version': data.validated_data['version']})
        agent.hostname = data.validated_data['hostname']
        agent.version = data.validated_data['version']
        agent.save(update_fields=['hostname', 'version', 'last_seen'])

        Metric.objects.create(agent=agent,
                              cpu=data.validated_data['cpu'],
                              mem=data.validated_data['mem'],
                              disk=data.validated_data['disk'],
                              captured_at=timezone.now())

        pending = list(agent.commands.filter(status='pending').values('id', 'type', 'payload'))
        return Response({'commands': pending})

class CommandResult(APIView):
    def post(self, request, pk):
        cmd = get_object_or_404(Command, pk=pk)
        serializer = CommandResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cmd.status = serializer.validated_data['status']
        cmd.result = {'log': serializer.validated_data.get('log', '')}
        cmd.save(update_fields=['status', 'result', 'updated_at'])
        return Response({'ok': True})

class AgentList(APIView):
    def get(self, request):
        agents = Agent.objects.all()
        return Response(
            {
                'count': agents.count(),
                'agents': list(agents.values('uuid', 'hostname', 'version', 'last_seen'))
            })
