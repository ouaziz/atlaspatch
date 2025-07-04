from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Agent, Command, Metric, Inventory
from .serializers import HeartbeatSerializer, CommandResultSerializer, MetricSerializer, AgentSerializer, CommandSerializer, CommandCreateSerializer, InventorySerializer   
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.response import Response
from .utils.jwt import make_access_token
from .auth import JWTAuth

class AgentLogin(APIView):
    authentication_classes = []       # mTLS fait déjà l’auth
    permission_classes     = []

    def post(self, request):
        agent_id = request.client_cert.subject.rfc4514_string()  # ex.
        access = make_access_token(agent_id)
        return Response({"access": access})

class Heartbeat(APIView):
    authentication_classes = [JWTAuth]   # le token courant est vérifié
    permission_classes     = []
    def post(self, request):
        serializer = HeartbeatSerializer(data=request.data)   # ①
        serializer.is_valid(raise_exception=True)             # ② validation
        data = serializer.validated_data  
        hardware_uuid = data['hardware_uuid']
        agent, _ = Agent.objects.get_or_create(hardware_uuid=hardware_uuid,
                                               defaults={'hostname': data['hostname'],
                                                         'version': data['version']})
        agent.hostname = data['hostname']
        agent.version = data['version']
        agent.save(update_fields=['hostname', 'version', 'last_seen'])

        Metric.objects.create(agent=agent,
                              cpu=data['cpu'],
                              mem=data['mem'],
                              disk=data['disk'],
                              captured_at=timezone.now())

        pending = list(agent.commands.filter(status='pending').values('id', 'type', 'payload'))

        to_insert = [
            Inventory(
                agent=agent,
                name=item["name"],
                version=item["version"],
                captured_at=item["captured_at"],
            )
            for item in data["inventory"]
        ]

        Inventory.objects.bulk_create(
            to_insert,
            update_conflicts=True,
            unique_fields=["agent", "name"],
            update_fields=["version", "captured_at"],
        )
        # return Response({"status": "success", "data": pending}, status=status.HTTP_200_OK)
        # Si le token expire dans < 5 min, renvoyer un nouveau
        ttl = request.auth["exp"] - int(time.time())
        if ttl < 300:
            new_token = make_access_token(request.auth["sub"])
            return Response({"status": "success", "access": new_token})
        return Response({"status": "success"})

class CommandResult(APIView):
    authentication_classes = [JWTAuth]   # le token courant est vérifié
    permission_classes     = []
    def post(self, request, pk):
        cmd = get_object_or_404(Command, pk=pk)
        serializer = CommandResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        cmd.status = serializer.validated_data['status']
        cmd.result = {'log': serializer.validated_data.get('log', '')}
        cmd.save(update_fields=['status', 'result', 'updated_at'])
        return Response({"status": "success"}, status=status.HTTP_200_OK)

class CommandServerList(APIView):
    authentication_classes = [JWTAuth]   # le token courant est vérifié
    permission_classes     = []
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
    authentication_classes = [JWTAuth]   # le token courant est vérifié
    permission_classes     = []
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
    authentication_classes = [JWTAuth]   # le token courant est vérifié
    permission_classes     = []
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
    authentication_classes = [JWTAuth]   # le token courant est vérifié
    permission_classes     = []
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
    authentication_classes = [JWTAuth]   # le token courant est vérifié
    permission_classes     = []
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
    authentication_classes = [JWTAuth]   # le token courant est vérifié
    permission_classes     = []
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
    authentication_classes = [JWTAuth]   # le token courant est vérifié
    permission_classes     = []
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