import json
from django.test import TestCase, Client
from django.core.paginator import Paginator
from .models import User, Category
from selenium import webdriver


# Create your tests here.
class PostTestCase(TestCase):
    def setUp(self):
        # Create users.
        u1 = User.objects.create_user(username="u1", email="u1@seidai.com", password="pass1234")
        u2 = User.objects.create_user(username="u2", email="u2@seidai.com", password="pass1234")
        u3 = User.objects.create_user(username="u3", email="u3@seidai.com", password="pass1234")
    
        # Create posts.
        cat_1 = Category.objects.create(name="test")
        
    def test_cat_count(self):
        u = User.objects.get(username="u1")
        self.assertEqual(Category.objects.all().count(), 1)