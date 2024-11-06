from pymongo import MongoClient
 
myClient=MongoClient("mongodb://localhost:27017")
mydatabase=myClient['foodDelivery']
dishes_collection = mydatabase['Dishes']
category_collection = mydatabase['Categories']  # Collection for categories
subcategory_collection = mydatabase['Subcategories']