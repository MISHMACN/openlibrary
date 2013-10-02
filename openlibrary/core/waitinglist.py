"""Implementation of waiting-list feature for OL loans.

Each waiting instance is represented as a document in the store as follows:

    {
        "_key": "waiting-loan-OL123M-anand",
        "type": "waiting-loan",
        "user": "/people/anand",
        "book": "/books/OL123M",
        "status": "waiting",
        "since": "2013-09-16T06:09:16.577942",
        "last-update": "2013-10-01T06:09:16.577942"
    }
"""
import datetime
import web

def get_waitinglist_for_book(book_key):
    """Returns the lost of  records for the users waiting for given book.

    This is admin-only feature. Works only if the current user is an admin.
    """
    return web.ctx.site.store.values(type="waiting-loan", name="book", value=book_key, limit=1000)

def get_waitinglist_size(book_key):
    """Returns size of the waiting list for given book.
    """
    keys = web.ctx.site.store.keys(type="waiting-loan", name="book", value=book_key, limit=1000)
    return len(keys)

def get_waitinglist_for_user(user_key):
    """Returns the list of records for all the books that a user is waiting for.
    """
    return web.ctx.site.store.values(type="waiting-loan", name="user", value=user_key, limit=1000)

def is_user_waiting_for(user_key, book_key):
    """Returns True if the user is waiting for specified book.
    """
    ukey = user_key.split("/")[-1]
    bkey = book_key.split("/")[-1]
    key = "waiting-loan-%s-%s" % (ukey, bkey)
    doc = web.ctx.site.store.get(key)
    return doc and doc['status'] != 'expired'

def get_waitinglist_position(user_key, book_key):
    ukey = user_key.split("/")[-1]
    bkey = book_key.split("/")[-1]
    key = "waiting-loan-%s-%s" % (ukey, bkey)

    wl = get_waitinglist_for_book(book_key)
    keys = [doc['_key'] for doc in sorted(wl, key=lambda doc: doc['since'])]
    try:
        # Adding one to start the position from 1 instead of 0
        return keys.index(key) + 1
    except ValueError:
        return -1

def join_waitinglist(user_key, book_key):
    """Adds a user to the waiting list of given book.

    It is done by createing a new record in the store.
    """
    ukey = user_key.split("/")[-1]
    bkey = book_key.split("/")[-1]
    key = "waiting-loan-%s-%s" % (ukey, bkey)
    timestamp = datetime.datetime.utcnow().isoformat()

    d = {
        "_key": key,
        "type": "waiting-loan",
        "user": user_key,
        "book": book_key,
        "status": "waiting",
        "since": timestamp,
        "last-update": timestamp        
    }
    web.ctx.site.store[key] = d

def leave_waitinglist(user_key, book_key):
    """Removes the given user from the waiting list of the given book.
    """
    ukey = user_key.split("/")[-1]
    bkey = book_key.split("/")[-1]
    key = "waiting-loan-%s-%s" % (ukey, bkey)
    web.ctx.site.store.delete(key)
    