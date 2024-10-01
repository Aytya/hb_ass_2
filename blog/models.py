from django.db import models
from django.contrib.auth.models import User, AbstractUser

# Create your models here.

class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True, null=True)

    groups = models.ManyToManyField('auth.Group', related_name='blog_users', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='blog_users_permissions', blank=True)

    def __str__(self):
        return f"{self.username} ({self.email})"

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag', blank=True, related_name='posts')

    class Meta:
        indexes = [models.Index(fields=['author'])]

    def __str__(self):
        return f"Post: {self.title} by {self.author.username}"

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['post', 'created_at'])]

    def __str__(self):
        return f'Comment by {self.author.username} on {self.post.title}'

class RoundRobinMiddleware:
    servers = ['http://localhost:8001', 'http://localhost:8002']
    index = 0

    def get_next_server(self):
        server = self.servers[self.index]
        self.index = (self.index + 1) % len(self.servers)
        return server

