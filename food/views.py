from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from pymongo import MongoClient
from bson.objectid import ObjectId
from .models import Dish, Category, Subcategory
from .serializers import DishSerializer, CategorySerializer, SubcategorySerializer

import logging

logger = logging.getLogger(__name__)

# MongoDB Client
myClient=MongoClient("mongodb://localhost:27017")
mydatabase=myClient['foodDelivery']
dishes_collection = mydatabase['Dishes']
category_collection = mydatabase['Categories']  # Collection for categories
subcategory_collection = mydatabase['Subcategories']

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def create(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            # Prepare data for MongoDB insertion
            mongo_data = {
                "name": serializer.validated_data.get("name"),
            }

            # Insert into MongoDB
            inserted_data = category_collection.insert_one(mongo_data)

            # Save to Django's database (for API tracking)
            category_instance = Category.objects.create(
                name=serializer.validated_data.get("name")
            )

            # Return both MongoDB and Django response for API purposes
            response_data = serializer.data
            response_data['_id'] = str(inserted_data.inserted_id)  # MongoDB ID
            return Response(response_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer

    def create(self, request):
        serializer = self.get_serializer_class()(data=request.data)
        if serializer.is_valid():
            mongo_data = {
                "name": serializer.validated_data.get("name"),
                "parent_category": str(serializer.validated_data.get("parent_category").id) if serializer.validated_data.get("parent_category") else None
            }
            
            # Insert into MongoDB
            inserted_data = subcategory_collection.insert_one(mongo_data)

            # Save to Django's database (for API tracking)
            subcategory_instance = Subcategory.objects.create(
                name=serializer.validated_data.get("name"),
                parent_category=serializer.validated_data.get("parent_category")
            )
            
            response_data = serializer.data
            response_data['_id'] = str(inserted_data.inserted_id)  # MongoDB ID
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer

    def create(self, request):
        logger.info(f"Request Data: {request.data}")
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                image_data = request.FILES.get('image')
                category = serializer.validated_data['category']
    
                # Create a Dish instance with the is_available field included
                dish_instance = Dish.objects.create(
                    name=serializer.validated_data['name'],
                    description=serializer.validated_data['description'],
                    price=serializer.validated_data['price'],
                    category=category,
                    subcategory=serializer.validated_data['subcategory'],
                    preparation_time=serializer.validated_data['preparation_time'],
                    image=image_data,
                    is_available=serializer.validated_data.get('is_available', True)  # Set default to True if not provided
                )
    
                # Save to MongoDB
                dishes_collection.insert_one({
                    'name': dish_instance.name,
                    'description': dish_instance.description,
                    'price': float(dish_instance.price),
                    'category': category.name,
                    'subcategory': str(dish_instance.subcategory.id),
                    'preparation_time': dish_instance.preparation_time,
                    'is_available': dish_instance.is_available,
                    'image': dish_instance.image.url if dish_instance.image else None
                })
    
                return Response(DishSerializer(dish_instance).data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Error creating dish: {e}")  # Log the error
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    

    def retrieve(self, request, pk=None):
        if not ObjectId.is_valid(pk):
            return Response({'msg': 'Invalid ID format'}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve from MongoDB
        existing_item = dishes_collection.find_one({"_id": ObjectId(pk)})
        if not existing_item:
            return Response({'msg': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

        # Convert ObjectId to string before returning
        existing_item["_id"] = str(existing_item["_id"])
        return Response(existing_item, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        existing_item = dishes_collection.find_one({"_id": ObjectId(pk)})
        if existing_item:
            # Update the fields based on the request data
            updated_item = {
                "name": request.data.get('name', existing_item.get('name', '')),
                "category": request.data.get('category', existing_item.get('category', '')),
                "description": request.data.get('description', existing_item.get('description', '')),
                "price": request.data.get('price', existing_item.get('price', 0)),
                "is_available": request.data.get('is_available', existing_item.get('is_available', False)),
            }
            # Update the item in the collection
            dishes_collection.update_one({"_id": ObjectId(pk)}, {"$set": updated_item})
            return Response(updated_item, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Dish not found."}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
        result = dishes_collection.delete_one({"_id": ObjectId(pk)})
        if result.deleted_count == 1:
            return Response(status=status.HTTP_204_NO_CONTENT)  # No Content
        else:
            return Response({"error": "Dish not found."}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request):
        dishes = dishes_collection.find()
        dishes_list = [{'id': str(dish['_id']), 'name': dish['name'], 'description': dish['description'], 'category': dish['category'], 'price': dish['price'], 'image':dish['image'], 'is_available':dish['is_available']} for dish in dishes]
        return Response(dishes_list)