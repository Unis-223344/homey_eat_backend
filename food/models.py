from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name

class Subcategory(models.Model):
    name = models.CharField(max_length=30)
    parent_category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Dish(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(Category, related_name='dishes', on_delete=models.CASCADE)
    subcategory = models.ForeignKey(Subcategory, related_name='dishes', on_delete=models.CASCADE)
    description = models.TextField(max_length=200)
    ingredients = models.TextField(blank=True)
    # quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    preparation_time = models.PositiveIntegerField()
    image = models.ImageField(upload_to='dishes/', blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name
