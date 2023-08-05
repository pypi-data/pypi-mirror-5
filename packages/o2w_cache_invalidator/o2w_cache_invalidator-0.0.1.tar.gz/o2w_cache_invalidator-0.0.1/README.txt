===========
cache invalidator
===========

Invalidates caches when a change occurs in any model.

INSTALLED_APPS += (
    'o2w.cache_invalidador',
)
O2W_CACHE_INVALIDATOR = {
    "memcached": True,
    "varnish": "url to varnish",
    "domain": "domain (normally same as above)",
}
