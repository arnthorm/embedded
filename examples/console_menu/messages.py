from embedded.helpers import enum

msgs = enum(
  echo=0,
)

message_collection = {
  msgs.echo: {
    'name': 'Echo',
    'fields': ('text', ),
    'types': ('%ds',),
    'has_array': True,
  },
}
