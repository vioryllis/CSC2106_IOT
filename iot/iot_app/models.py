from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, floor=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not name:
            raise ValueError('The Name field must be set')

        email = self.normalize_email(email)
        user = self.model(email=email, name=name, floor=floor, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    class Meta:
        db_table = "user"
        # managed = False
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    floor = models.CharField(max_length=50)
    
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name

class Plant(models.Model):
    class Meta:
        db_table = "plant"
        # managed = False
    plant_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plants')
    name = models.CharField(max_length=100)
    floor = models.CharField(max_length=50)
    public = models.BooleanField(default=False)
    last_watered = models.DateTimeField(default=timezone.now)
    last_fertilized = models.DateTimeField(default=timezone.now)
    auto_system = models.BooleanField(default=False)
    min_water_level = models.DecimalField(max_digits=5, decimal_places=2)
    amt_to_water = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name

class SensorData(models.Model):
    class Meta:
        db_table = "sensordata"
        # managed = False
    sensor_data_id = models.AutoField(primary_key=True)
    water_level = models.DecimalField(max_digits=5, decimal_places=2)
    nutrient_level = models.DecimalField(max_digits=5, decimal_places=2)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE, related_name='sensor_data')
    
    def __str__(self):
        return f"{self.plant.name} Sensor Data"
