from django import template
from django.db import models
from django.core.cache import cache

register = template.Library()

Chunk = models.get_model('chunks', 'chunk')
CACHE_PREFIX = "chunk_"

def do_chunk(parser, token):
    # split_contents() knows not to split quoted strings.
    tokens = token.split_contents()
    if len(tokens) < 3 or len(tokens) > 4:
        raise template.TemplateSyntaxError, "%r tag should have either 3 or 4 arguments" % (tokens[0],)
    if len(tokens) == 3:
        tag_name, key, site = tokens
        cache_time = 0
    if len(tokens) == 4:
        tag_name, key, site, cache_time = tokens
    key = ensure_quoted_string(key, "%r tag's argument should be in quotes" % tag_name)
    return ChunkNode(key, site, cache_time)

class ChunkNode(template.Node):
    def __init__(self, key, site, cache_time=0):
       self.key = key
       self.site = template.Variable(site)
       self.cache_time = cache_time

    def render(self, context):
        site = self.site.resolve(context)
        
        try:
            cache_key = CACHE_PREFIX + self.key
            c = cache.get(cache_key)
            if c is None:
                c = Chunk.objects.get(key=self.key, site=site)
                cache.set(cache_key, c, int(self.cache_time))
            content = c.content
        except Chunk.DoesNotExist:
            content = ''
        return content


def do_get_chunk(parser, token):
    tokens = token.split_contents()
    if len(tokens) != 4 or tokens[2] != 'as':
        raise template.TemplateSyntaxError, 'Invalid syntax. Usage: {%% %s "key" as varname %%}' % tokens[0]
    tagname, key, site, varname = tokens[0], tokens[1], tokens[2], tokens[4]
    key = ensure_quoted_string(key, "Key argument to %r must be in quotes" % tagname)
    return GetChunkNode(key, site, varname)

class GetChunkNode(template.Node):
    def __init__(self, key, site, varname):
        self.key = key
        self.site = template.Variable(site)
        self.varname = varname

    def render(self, context):
        try:
            site = self.site.resolve(context)
            chunk = Chunk.objects.get(key=self.key, site=site)
        except Chunk.DoesNotExist:
            chunk = None
        context[self.varname] = chunk
        return ''


def ensure_quoted_string(string, error_message):
    '''
    Check to see if the key is properly double/single quoted and
    returns the string without quotes
    '''
    if not (string[0] == string[-1] and string[0] in ('"', "'")):
        raise template.TemplateSyntaxError, error_message
    return string[1:-1]


register.tag('chunk', do_chunk)
register.tag('get_chunk', do_get_chunk)
