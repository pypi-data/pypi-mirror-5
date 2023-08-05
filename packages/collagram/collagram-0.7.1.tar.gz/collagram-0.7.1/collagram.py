import os
import cStringIO
from datetime import datetime
import urllib

from instagram.bind import InstagramAPIError
from instagram.client import InstagramAPI

from PIL import Image

INSTAGRAM_TOKEN = os.environ.get('INSTAGRAM_TOKEN')
PATH_USERS = os.path.join(os.path.dirname(__file__), 'users')
PATH_TAGS = os.path.join(os.path.dirname(__file__), 'tags')
SIZE_DICT = {
    'thumbnail': 150,
    'low_resolution': 306,
    'standard_resolution': 612
}


class InvalidUserError(Exception):
    pass


class PrivateUserError(Exception):
    pass


class InvalidTagError(Exception):
    pass


class Collage(object):

    def __init__(self, username=None, tag=None, token=INSTAGRAM_TOKEN,
                 columns=10, rows=2, size='thumbnail',  path_users=PATH_USERS,
                 path_tags=PATH_TAGS):

        if username and tag:
            raise AttributeError('You may not specify both username and tag')

        if not username and not tag:
            raise AttributeError('You must specify either username and tag')

        if token is None:
            raise Exception('INSTAGRAM_TOKEN environment variable or the `token` attribute must be set.')

        self.api = InstagramAPI(access_token=token)

        self.username = username
        self.tag = tag
        self.path_users = path_users
        self.path_tags = path_tags
        self.columns = columns
        self.rows = rows
        self.size = size if size in SIZE_DICT else 'thumbnail'
        self.dimension = SIZE_DICT.get(self.size, 150)
        self.width = self.columns * self.dimension
        self.height = self.rows * self.dimension

    @property
    def name(self):
        """Return canonical name

        Username or tag prefixed with @ or # respectively.
        """

        if self.username:
            return '@%s' % self.username
        elif self.tag:
            return '#%s' % self.tag
        else:
            return None

    @property
    def user_id(self):
        """Retrieve user id from username

        Search for username via api and then check for matching
        username. If found return id, otherwise throw 404.
        """

        if self.username:
            rv = self.api.user_search(q=self.username)
            for result in rv:
                if self.username == result.username:
                    return result.id
        return None

    @property
    def filename(self):
        """Return generated filename."""

        if self.username:
            return os.path.join(self.path_users, "%s_%s.jpg" % (self.username, self.size))
        elif self.tag:
            return os.path.join(self.path_tags, "%s_%s.jpg" % (self.tag, self.size))
        else:
            return None

    def is_valid(self):
        """Check if the username is valid."""

        if not self.user_id:
            return False
        return True

    def is_cached(self):
        """Check for existing version of file"""

        return True if os.path.exists(self.filename) else False

    def is_stale(self, seconds=60):
        """Check if the cached file is a certain age

        Check if the file is younger than the number of seconds
        specified. Return True for youger, False for older.
        """

        modified = datetime.fromtimestamp(os.path.getmtime(self.filename))
        age = datetime.now() - modified
        fresh = True if age.seconds < seconds else False
        return fresh

    def fetch(self, force=False):
        """Return filename, generating if necessary

        Check if there is a chached version. If a cached version
        doesn't exists or `force` is True we generate one. Otherwise
        we just return the filename.

        """

        if not self.is_cached() or force:
            self.generate()
        return self.filename

    def media_json(self):
        """Username/tag specific JSON from instagram's API."""

        if self.user_id:
            try:
                return self.api.user_recent_media(user_id=self.user_id)[0]
            except InstagramAPIError as e:
                if e.status_code == 400:
                    raise PrivateUserError("You don't have permission to view this user")
                else:
                    raise Exception('Unknow status: %s, Message: %s' % (e.status_code, e.error_message))
            except:
                raise Exception

        elif self.tag:
            try:
                return self.api.tag_recent_media(tag_name=self.tag)[0]
            except InstagramAPIError as e:
                raise InvalidTagError('Unable to find tag')
            except:
                raise Exception

        else:
            return None

    def media_urls(self):
        """List of instagram image URLS"""

        return [m.images[self.size].url for m in self.media_json()]

    def ensure_path(self):
        """Ensure that the path `self.generate()` will write to exists"""

        if self.username and not os.path.exists(self.path_users):
            os.makedirs(self.path_users)

        if self.tag and not os.path.exists(self.path_tags):
            os.makedirs(self.path_tags)

    def generate_or_queue(self, queue_func=None, seconds=86400):
        """Queue the generation if cached version is stale.

        This is useful when you don't want to wait on the `generate`
        function, if a cached version exists. If the cached version is
        fresh, we pass. If it is stale we queue up a new one to be
        generated.  If there is no cached version, one has to be
        generated right away. Just pass in your queue function and
        away we go!
        """

        if queue_func is None:
            raise Exception("Function must be provided.")

        if self.is_cached():
            if self.is_stale(seconds=seconds):
                queue_func(self.generate)
        else:
            self.generate()

    def generate(self):
        """Generate a collage

        Use instagram api to get the recent media json for a username
        or tag. Then download the images and stick them in temp files
        and places them into a blank image. The image is saved to disk
        after all collage is created.
        """

        blank_image = Image.new("RGB", (self.width, self.height))
        if not self.is_valid():
            raise InvalidUserError("User %s does not exist." % self.username)


        x = y = 0
        for idx, url in enumerate(self.media_urls()):
            image_data = cStringIO.StringIO(urllib.urlopen(url).read())
            image = Image.open(image_data)
            blank_image.paste(image, (x, y))
            x += self.dimension
            if idx == (self.columns - 1):
                x = 0
                y += self.dimension

        self.ensure_path()
        blank_image.save(self.filename)
