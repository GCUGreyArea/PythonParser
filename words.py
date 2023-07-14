#!/usr/bin/env python3

"""Fetch and print words from a URL

Usage: 
    python3 words.py <URL>
"""

from urllib.request import urlopen
import sys

def get_words(URL):
    """Fetch a list of words from a URL

    Args:
        url: The URL of a UTF-8 text document

    Returns: 
        A list of strings containing the words 
        from the document 
    """
    story = urlopen(URL)

    story_words = []
    for line in story:
        line_words = line.decode('utf8').split()
        for word in line_words:
            story_words.append(word)

    story.close()
    return story_words

def print_items(List):
    """Print a items one per line

    Args: 
        An iterable series of printable items
    """
    for Item in List:
        print(Item)

def main(Url):
    """Print each word from a text document from a URL

    Args: 
        url: The URL of a UTF-8 text document
    """   
    words = get_words(Url)
    print_items(words)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('please supply a RUL')
    else:
        main(sys.argv[1])
