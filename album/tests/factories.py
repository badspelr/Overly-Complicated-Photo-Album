"""
Test factories for creating test data.
"""
import factory
from django.contrib.auth.models import User
from factory.django import DjangoModelFactory
from ..models import Album, Photo, Video, Category, SiteSettings


class UserFactory(DjangoModelFactory):
    """Factory for creating User instances."""
    
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Hash password after user creation."""
        if not create:
            return
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password('defaultpassword123')


class CategoryFactory(DjangoModelFactory):
    """Factory for creating Category instances."""
    
    class Meta:
        model = Category
    
    name = factory.Sequence(lambda n: f"category{n}")
    description = factory.Faker('text', max_nb_chars=200)
    created_by = factory.SubFactory(UserFactory)


class AlbumFactory(DjangoModelFactory):
    """Factory for creating Album instances."""
    
    class Meta:
        model = Album
    
    title = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=500)
    owner = factory.SubFactory(UserFactory)
    category = factory.SubFactory(CategoryFactory)
    is_public = False


class PhotoFactory(DjangoModelFactory):
    """Factory for creating Photo instances."""
    
    class Meta:
        model = Photo
    
    title = factory.Faker('sentence', nb_words=2)
    description = factory.Faker('text', max_nb_chars=300)
    album = factory.SubFactory(AlbumFactory)
    category = factory.SubFactory(CategoryFactory)
    image = factory.django.ImageField()


class VideoFactory(DjangoModelFactory):
    """Factory for creating Video instances."""
    
    class Meta:
        model = Video
    
    title = factory.Faker('sentence', nb_words=2)
    description = factory.Faker('text', max_nb_chars=300)
    album = factory.SubFactory(AlbumFactory)
    category = factory.SubFactory(CategoryFactory)
    video = factory.django.FileField()


class SiteSettingsFactory(DjangoModelFactory):
    """Factory for creating SiteSettings instances."""
    
    class Meta:
        model = SiteSettings
    
    title = factory.Faker('sentence', nb_words=2)
    description = factory.Faker('text', max_nb_chars=200)
