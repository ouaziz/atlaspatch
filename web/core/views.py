from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Agent, Command, Metric, Inventory
from .serializers import HeartbeatSerializer, CommandResultSerializer, MetricSerializer, AgentSerializer, CommandSerializer, CommandCreateSerializer, InventorySerializer   


class Heartbeat(APIView):
    def post(self, request):
        data = HeartbeatSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        hardware_uuid = data.validated_data['hardware_uuid']
        agent, _ = Agent.objects.get_or_create(hardware_uuid=hardware_uuid,
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

        # Metric.objects.update_or_create(
        #     agent=agent,
        #     day_bucket=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0),
        #     defaults=dict(
        #         captured_at=timezone.now(),
        #         cpu=data.validated_data['cpu'],
        #         mem=data.validated_data['mem'],
        #         disk=data.validated_data['disk'],
        #     )
        # )
        pending = list(agent.commands.filter(status='pending').values('id', 'type', 'payload'))

        # update inventory
        Inventory.objects.create(agent=agent,
                                 name=data.validated_data['inventory'][0]['name'],
                                 version=data.validated_data['inventory'][0]['version'],
                                 captured_at=timezone.now())
        return Response({'commands': pending})

class CommandResult(APIView):
    def post(self, request, pk):
        cmd = get_object_or_404(Command, pk=pk)
        serializer = CommandResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cmd.status = serializer.validated_data['status']
        cmd.result = {'log': serializer.validated_data.get('log', '')}
        cmd.save(update_fields=['status', 'result', 'updated_at'])
        return Response({'status': 'success'})

class CommandServerList(APIView):
    def get(self, request, uuid):
        try:
            commands = CommandSerializer(Command.objects.filter(agent=uuid), many=True)
            return Response(
                {
                    'status': 'success',
                    'data': commands.data
                })
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': str(e)
                })

class CommandCreate(APIView):
    def post(self, request):
        try:
            serializer = CommandCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            command = serializer.save()
            return Response(
                {
                'status': 'success',
                'data': CommandSerializer(command).data
            })
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': str(e)
                })

# agents
class AgentList(APIView):
    def get(self, request):
        try:
            agents = AgentSerializer(Agent.objects.all(), many=True)
            return Response(
                {
                    'status': 'success',
                    'data': agents.data
                })
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': str(e)
                })

class MetricDetail(APIView):
    def get(self, request, pk):
        try:
            metric = MetricSerializer(Metric.objects.get(pk=pk))
            return Response(
                {
                    'status': 'success',
                    'data': metric.data
                })
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': str(e)
                })
        

class MetricServerDetail(APIView):
    def get(self, request, uuid):
        try:
            metric = MetricSerializer(Metric.objects.filter(agent=uuid), many=True)
            return Response(
                {
                    'status': 'success',
                    'data': metric.data
                })
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': str(e)
                })
    
class InventoryDetail(APIView):
    def get(self, request, pk):
        try:
            inventory = InventorySerializer(Inventory.objects.get(pk=pk))
            return Response(
                {
                    'status': 'success',
                    'data': inventory.data
                })
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': str(e)
                })
    
class InventoryServerDetail(APIView):
    def get(self, request, uuid):
        try:
            inventory = InventorySerializer(Inventory.objects.filter(agent=uuid), many=True)
            return Response(
                {
                    'status': 'success',
                    'data': inventory.data
                })
        except Exception as e:
            return Response(
                {
                    'status': 'error',
                    'message': str(e)
                })