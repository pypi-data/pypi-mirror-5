##
# Copyright (C) 2013 Jessica T. (Tsyesika) <xray7224@googlemail.com>
# 
# This program is free software: you can redistribute it and/or modify 
# it under the terms of the GNU General Public License as published by 
# the Free Software Foundation, either version 3 of the License, or 
# (at your option) any later version. 
# 
# This program is distributed in the hope that it will be useful, 
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the 
# GNU General Public License for more details. 
# 
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
##

import datetime
import logging
import mimetypes
import os

from dateutil.parser import parse

from pypump.compatability import *
from pypump.models import (AbstractModel, Postable, Likeable, Commentable,
                           Deleteable, Shareable)

_log = logging.getLogger(__name__)

@implement_to_string
class Image(AbstractModel, Postable, Likeable, Shareable, Commentable, Deleteable):
    
    url = None
    actor = None
    author = actor
    summary = None
    display_name = None
    id = None
    updated = None
    published = None
    _links = None

    @property
    def ENDPOINT(self):
        return "/api/user/{username}/feed".format(self._pump.nickname)

    def __init__(self, id=None, url=None, display_name=None, content=None, 
                 actor=None, width=None, height=None, published=None,
                 updated=None, links=None, *args, **kwargs):

        super(Image, self).__init__(*args, **kwargs)

        self.id = id
        self.display_name = display_name
        self.content = content
        self.actor = actor or self.actor
        self.url = url
        self.published = published
        self.updated = updated
        self._links = links or []

    def __repr__(self):
        if self.actor is None:
            return "<{type}>".format(type=self.TYPE)

        return "<{type} by {webfinger}>".format(
            type=self.TYPE,
            webfinger=self.actor.webfinger)

    def __str__(self):
        return str(repr(self))

    def from_file(self, filename):
        """ Uploads an image from a filename """
        mimetype = mimetypes.guess_type(filename)[0] or "application/octal-stream"
        headers = {
            "Content-Type": mimetype,
            "Content-Length": os.path.getsize(filename),
        }

        params = {"qqfile": filename.split("/")[-1]}

        if self.display_name is not None:
            params["title"] = self.display_name
        if self.content is not None:
            params["description"] = self.content
        
        image = self._pump.request(
                "/api/user/{0}/uploads".format(self._pump.nickname),
                method="POST",
                data=open(filename).read(),
                headers=headers,
                params=params,
                )

        self.unserialize(image, obj=self)

        # now send it to the feed
        data = {
            "verb": "post",
            "object": image,
        }

        data.update(self.serialize())

        # send it to the feed
        image_feed = self._pump.request(
                "/api/user/{0}/feed".format(self._pump.nickname),
                method="POST",
                data=data,
                )

        _log.debug(image_feed)
        self.unserialize(image_feed)
        return self

    def unserialize(self, data):
        image_id = data.get("id", None)
        if "fullImage" in data:
            full_image = data["fullImage"]["url"]
            full_image = type(self)(id=image_id, url=full_image)
        else:
            full_image = None

        if "image" in data:
            image = data["image"]["url"]
            image = type(self)(id=image_id, url=image)
        else:
            image = None

        author = self._pump.Person().unserialize(data["author"]) if "author" in data else None

        links = dict()
        for i in ["likes", "replies", "shares"]:
            if data.get(i, None):
                if "pump_io" in data[i]:
                    links[i] = data[i]["pump_io"]["proxyURL"]
                else:
                    links[i] = data[i]["url"]

        for i in [full_image, image]:
            if i is None:
                continue
            i.actor = author
            i.published = parse(data["published"])
            i.updated = parse(data["updated"])
            i.display_name = data.get("displayName", u"")
            i.summary = data.get("summary", u"")
 
       # set the full and normal image on each one
        if full_image is not None:
            full_image.image = image
            full_image.original = full_image
            full_image._links = links

        if image is not None:
            image.image = image
            image.original = full_image
            image._links = links

        return image 
