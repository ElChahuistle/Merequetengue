import uuid

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


def get_default_user() -> User:
    """
    This callback method gets the User instance of user "anonymous" to be used when the
    original author was deleted.

    Note: This method is a proxy to allow the serialization of Pegoste class when
    being migrated to the DB.

    :return: The "anonymous" user

    Show username of default user

    >>> default_user = get_default_user()
    >>> default_user.username
    'anonymous'

    """
    return User.objects.get(username='anonymous')


def get_image_path(instance, filename: str) -> str:
    """
    This callback method returns the path in which images will be stored in MEDIA_ROOT directory. Using
    a universally unique identifier (UUID) to create unique folders for a user and pegoste. New images
    will be added, but previous ones won't be deleted.

    Note: This method is a proxy to allow the serialization of Pegoste class when
    being migrated to the DB.

    :param instance An object instance of Pegoste from which the user is being obtained.
    :param filename The name of the file uploaded.

    :return: The path in MEDIA_ROOT in which the image will be saved.
    """

    return '{user}/{uuid}/{file}'.format(user=instance.author.username, uuid=str(uuid.uuid4()), file=filename)


class Pegoste(models.Model):
    """
    Model to implement posts object in the application. Every attribute is mandatory.

    * title: The title of the post
    * subtitle: The sub-title of the post
    * publish_date: The date/time in which the post the post  was created.
    * author: Creator of the post. It is an implementation of User model for authentication porpoises.
    * content: The text of the post
    * image: A image part of the post

    Create new post

    >>> new_pegoste = Pegoste(
    ...     title='My Title',
    ...     subtitle='A new post',
    ...     author=User.objects.get(username='anonymous'),
    ...     content='Lorem ipsum dolor sit amet, consectetur adipiscing elit.'
    ... )
    >>> new_pegoste.save()

    Check if it exists if the post exists.

    >>> Pegoste.objects.filter(title='My Title').exists()
    True

    Update title and subtitle

    >>> new_pegoste.title = 'New Title'
    >>> new_pegoste.subtitle = 'New subtitle for new title'
    >>> new_pegoste.save()
    >>> new_pegoste
    <Pegoste: New Title>

    Delete post.

    >>> _ = Pegoste.objects.get(pk=new_pegoste.pk).delete()  # Delete object, but Skip operation's result
    >>> Pegoste.objects.filter(title='My Title').exists()
    False
    """

    title = models.CharField(max_length=50)
    subtitle = models.CharField(max_length=100, blank=True)
    publish_date = models.DateTimeField(default=timezone.now, editable=False)
    author = models.ForeignKey(User, on_delete=models.SET(get_default_user), editable=False)
    content = models.TextField()
    image = models.ImageField(upload_to=get_image_path, blank=True)
    slug = models.SlugField(max_length=50, editable=False)

    def get_absolute_url(self):
        """
        This method will be used by CreatePegoste and UpdatePegoste to redirect to the newly or updated Pegoste.
        Referencing URL setup pegoste to create the URL.

        :return: Absolute URL to current object.
        """

        return reverse('Fandango:pegoste', kwargs={'username': self.author.username, 'slug': self.slug})

    def __str__(self):
        return f'{self.title}'
