from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.db.models import Avg
import requests
from django.http import JsonResponse
from .models import User, Plant, SensorData
import random
import json
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.safestring import mark_safe
from decimal import Decimal

def register(request):
    if request.method == 'POST':
        # Retrieve form data
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        floor = request.POST.get('floor')
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            error_message = "Email already registered."
            return render(request, 'register.html', {'error_message': error_message})
        
        # Use the custom user manager to create a new user
        try:
            user = User.objects.create_user(email=email, name=name, password=password, floor=floor)
        except ValueError as e:
            error_message = str(e)
            return render(request, 'register.html', {'error_message': error_message})
        
        return redirect('login')
        
    else:
        # If it's a GET request, just display the registration form
        return render(request, 'register.html')
    
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('plants')
        else:
            error_message = "Invalid email or password."
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')
    
@login_required 
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required 
@csrf_exempt
def add_plant(request):
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('plantName')
        is_public = request.POST.get('isPublic')
        user_id = request.user.user_id 
        floor = request.user.floor
        default_value = 50
        
        # Save plant to database
        plant = Plant.objects.create(
            name=name,
            floor=floor,
            public=is_public,
            min_water_level=default_value,
            amt_to_water=default_value,
            user_id=user_id,
        )
        
        return JsonResponse({'success': True})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@csrf_exempt
def update_plant_name(request, plant_id):
    data = json.loads(request.body)
    try:
        plant = Plant.objects.get(pk=plant_id, user=request.user)
        plant.name = data.get('name')
        plant.save()
        return JsonResponse({"success": "Plant name updated successfully."})
    except Plant.DoesNotExist:
        return JsonResponse({"error": "Plant not found."}, status=404)

@login_required
@csrf_exempt
def update_plant_public(request, plant_id):
    data = json.loads(request.body)
    try:
        plant = Plant.objects.get(pk=plant_id, user=request.user)
        plant.public = data.get('public', False)
        plant.save()
        return JsonResponse({"success": "Plant public status updated successfully."})
    except Plant.DoesNotExist:
        return JsonResponse({"error": "Plant not found."}, status=404)

@login_required
def delete_plant(request, plant_id):
    try:
        plant = Plant.objects.get(pk=plant_id, user=request.user)
        plant.delete()
        return redirect('plants')  
    except Plant.DoesNotExist:
        return HttpResponse('Plant not found', status=404)

@login_required 
def plants(request):
    user_plants_only = 'true' == request.GET.get('user_plants', 'false').lower()
    
    if user_plants_only:
        plant_query = Plant.objects.filter(user=request.user)
    else:
        plant_query = Plant.objects.filter(public=True)
    
    plants = {}
    for plant in plant_query:
        if plant.floor not in plants:
            plants[plant.floor] = []
        plants[plant.floor].append(plant)
    
    context = {
        "plants": dict(sorted(plants.items(), key=lambda x: x[0])),
        "user_plants_only": user_plants_only,  # Pass this to the template to keep track of the current filter state
        "active_filter": "mine" if user_plants_only else "all",
    }
    return render(request, "plants.html", context)

@login_required 
def plant(request, plant_id):
    template = loader.get_template("plant.html")
    context = {
        "plant": Plant.objects.get(pk=plant_id),
    }
    return HttpResponse(template.render(context, request))

def dashboard(request):
    # Filter plants by the current user
    user_plants = Plant.objects.filter(user=request.user)
    total_user_plants = user_plants.count()

    # Get average sensor data for the user's plants
    sensor_data_qs = SensorData.objects.filter(plant__in=user_plants).values('plant__name').annotate(
        avg_water_level=Avg('water_level'),
        avg_nutrient_level=Avg('nutrient_level')
    )

    # Prepare the data for the bar chart
    plant_names = [entry['plant__name'] for entry in sensor_data_qs]
    avg_water_levels = [entry['avg_water_level'] for entry in sensor_data_qs]
    avg_nutrient_levels = [entry['avg_nutrient_level'] for entry in sensor_data_qs]

    # Serialize the data to JSON strings
    plant_names_json = mark_safe(json.dumps(plant_names, cls=DjangoJSONEncoder))
    avg_water_levels_json = mark_safe(json.dumps(avg_water_levels, cls=DjangoJSONEncoder))
    avg_nutrient_levels_json = mark_safe(json.dumps(avg_nutrient_levels, cls=DjangoJSONEncoder))

    context = {
        'total_user_plants': total_user_plants,
        'user': request.user,
        'plant_names': plant_names_json,
        'avg_water_levels': avg_water_levels_json,
        'avg_nutrient_levels': avg_nutrient_levels_json,
    }
    print(context)
    return render(request, 'dashboard.html', context)

@login_required
def index(request):
    template = loader.get_template("dashboard.html")
    context = {}
    if not User.objects.all():
        u = User(name="user", email="user@mail.com", password="password", floor="floor")
        u.save()

    if not Plant.objects.all():
        for i in range(10):
            p = Plant(name="Plant {}".format(i),
                      floor="{}".format(random.choice(["1", "2", "3", "4", "5"])),
                      public=True,
                      auto_system=random.choice([True, False]),
                      min_water_level=random.uniform(0, 100),
                      amt_to_water=random.uniform(0, 100),
                      user=User.objects.all()[0])
            p.save()

    return HttpResponse(template.render(context, request))


#########################################
###############  MQTT  ##################
#########################################
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
import threading
def publish_mqtt_message(request):
    # MQTT Broker settings
    mqtt_broker = "172.20.10.10"
    mqtt_port = 1883
    mqtt_topic = "M5Stack/1"
    mqtt_message = " u a bij frfr"

    # Publishing the message
    try:
        publish.single(mqtt_topic, mqtt_message, hostname=mqtt_broker, port=mqtt_port)
        return HttpResponse("Message published successfully.")
    except Exception as e:
        return HttpResponse(f"Failed to publish message: {e}")

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    topics = [("M5Stack/1", 0), ("M5Stack/2", 0)]  # List of topics with QoS level 0
    client.subscribe(topics)

def on_message(client, userdata, msg):
    message_str = msg.payload.decode('utf-8')
    topic_parts = msg.topic.split('/')
    if len(topic_parts) == 2:
        device_id = topic_parts[1]
        print(f"Received message from M5Stack {device_id}: {message_str}")
    else:
        print(f"Received message from unknown topic {msg.topic}: {message_str}")

def start_mqtt():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("172.20.10.10", 1883, 60)
    
    # Non-blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    client.loop_start()

def start_mqtt_listener(request):
    try:
        thread = threading.Thread(target=start_mqtt)
        thread.daemon = True  # Daemon threads exit when the program does
        thread.start()
        return HttpResponse("MQTT listener started")
    except Exception as e:
        return HttpResponse(f"Error starting MQTT listener: {e}")

#########################################
###############  MESH  ##################
#########################################

@csrf_exempt
def send_data(request):
    if request.method == 'POST':
        data = request.POST  # Assuming data is sent as form data
        print(data)
        # Process data received from the M5StickC device
        # Example:
        # YourModel.objects.create(**data)
        return JsonResponse({'message': 'Data received successfully'})
    else:
        return JsonResponse({'error': 'Only POST requests are allowed'})

@csrf_exempt
def get_data(request):
    if request.method == 'GET':
        # Retrieve data to be sent to the M5StickC device
        # Example:
        # data = YourModel.objects.all().values()
        data = {'example_key': 'example_value'}
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Only GET requests are allowed'})