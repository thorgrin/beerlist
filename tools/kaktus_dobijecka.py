#!/usr/bin/env python3

# Code from https://gitlab.stdin.cz/ps/kaktus-dobijecka

from bs4 import BeautifulSoup as bs
from collections import namedtuple
from typing import List
import ssl
import requests
import os
import sys
import json


def storage_factory(cls_name: str, properties: List[str] = None):
    if properties is None:
        properties = []

    def __init__(self, file: str) -> None:
        self._file = file
        try:
            with open(self._file, 'r') as f:
                self._content = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self._content = {}

    def flush(self) -> None:
        with open(self._file, 'w') as f:
            json.dump(self._content, f, ensure_ascii=False)

    cls_attrs = dict(__init__=__init__,
                     flush=flush)

    def get_property(name: str) -> property:
        def getter(self) -> str:
            content = self.__dict__["_content"]
            return content[name] if name in content else ""

        def setter(self, value: str) -> None:
            self.__dict__["_content"][name] = value

        return property(getter, setter)

    for prop in properties:
        cls_attrs[prop] = get_property(prop)

    return type(cls_name, (object,), cls_attrs)


Message = namedtuple("Message", ["title", "text"])
Storage = storage_factory("Storage", ["last_seen_title"])

def parse_html_for_new_messages(response: str,
                                last_seen_title: str) -> List[Message]:
    new_content = []
    soup = bs(response, "lxml")

    for element in soup.find_all('div', {'class': 'article'}):
        title = element.h3.string
        text = '\n'.join([a.string for a in element.find_all('p') if a.string])

        # All new messages are already read
        if title == last_seen_title:
            break
        # Place new message to send queue
        else:
            new_content.append(Message(title, text))

    return new_content


def main() -> None:
    # create storage object
    store = Storage(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                 '../cache/kaktus.json'))

    # fetch the Kaktus URL and check if it was successful
    try:
        kaktus_response = requests.get(
            'https://www.mujkaktus.cz/novinky',
            timeout=10.0)
        if kaktus_response.status_code == 200:
            response_text = kaktus_response.text
        else:
            print("The page was not successfully loaded. Http code: {}"
                  .format(kaktus_response.status_code))
            sys.exit(2)

    except Exception as e:
        print("The page was not successfully loaded. Error: {}".format(e))
        sys.exit(2)

    # parse the html, get new messages
    new_content = parse_html_for_new_messages(response_text,
                                              store.last_seen_title)

    # if something new appeared
    if len(new_content) > 0:
        # store last seen item to the store
        store.last_seen_title = new_content[0].title
        store.flush()

        # print new message
        print(new_content[0].title + ' | ' + new_content[0].text)


if __name__ == '__main__':
    main()
