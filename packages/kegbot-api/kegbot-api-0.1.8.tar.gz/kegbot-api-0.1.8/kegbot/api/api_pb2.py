# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: api.proto

from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)


import models_pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='api.proto',
  package='',
  serialized_pb='\n\tapi.proto\x1a\x0cmodels.proto\"1\n\x04Meta\x12\r\n\x05total\x18\x01 \x01(\r\x12\r\n\x05limit\x18\x02 \x01(\r\x12\x0b\n\x03pos\x18\x03 \x01(\r\"r\n\x17UserRegistrationRequest\x12\x10\n\x08username\x18\x01 \x02(\t\x12\r\n\x05\x65mail\x18\x02 \x02(\t\x12\x10\n\x08password\x18\x03 \x01(\t\x12\x0e\n\x06gender\x18\x04 \x01(\t\x12\x14\n\x0ctwitter_name\x18\x05 \x01(\t\"\xef\x01\n\x12RecordDrinkRequest\x12\x10\n\x08tap_name\x18\x01 \x01(\t\x12\r\n\x05ticks\x18\x02 \x02(\r\x12\x11\n\tvolume_ml\x18\x03 \x01(\x02\x12\x10\n\x08username\x18\x04 \x01(\t\x12\x16\n\x0bseconds_ago\x18\x05 \x01(\r:\x01\x30\x12\x13\n\x0brecord_date\x18\x06 \x01(\t\x12\x18\n\x10\x64uration_seconds\x18\x07 \x01(\r\x12\x12\n\nauth_token\x18\x08 \x01(\t\x12\x0f\n\x07spilled\x18\t \x01(\x08\x12\r\n\x05shout\x18\n \x01(\t\x12\x18\n\x10tick_time_series\x18\x0b \x01(\t\"T\n\x18RecordTemperatureRequest\x12\x13\n\x0bsensor_name\x18\x01 \x02(\t\x12\x0e\n\x06temp_c\x18\x02 \x02(\x02\x12\x13\n\x0brecord_date\x18\x03 \x01(\tB\x12\n\x10org.kegbot.proto')




_META = _descriptor.Descriptor(
  name='Meta',
  full_name='Meta',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='total', full_name='Meta.total', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='limit', full_name='Meta.limit', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='pos', full_name='Meta.pos', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=27,
  serialized_end=76,
)


_USERREGISTRATIONREQUEST = _descriptor.Descriptor(
  name='UserRegistrationRequest',
  full_name='UserRegistrationRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='username', full_name='UserRegistrationRequest.username', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='email', full_name='UserRegistrationRequest.email', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='password', full_name='UserRegistrationRequest.password', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gender', full_name='UserRegistrationRequest.gender', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='twitter_name', full_name='UserRegistrationRequest.twitter_name', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=78,
  serialized_end=192,
)


_RECORDDRINKREQUEST = _descriptor.Descriptor(
  name='RecordDrinkRequest',
  full_name='RecordDrinkRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='tap_name', full_name='RecordDrinkRequest.tap_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='ticks', full_name='RecordDrinkRequest.ticks', index=1,
      number=2, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='volume_ml', full_name='RecordDrinkRequest.volume_ml', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='username', full_name='RecordDrinkRequest.username', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='seconds_ago', full_name='RecordDrinkRequest.seconds_ago', index=4,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=True, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='record_date', full_name='RecordDrinkRequest.record_date', index=5,
      number=6, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='duration_seconds', full_name='RecordDrinkRequest.duration_seconds', index=6,
      number=7, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='auth_token', full_name='RecordDrinkRequest.auth_token', index=7,
      number=8, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='spilled', full_name='RecordDrinkRequest.spilled', index=8,
      number=9, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='shout', full_name='RecordDrinkRequest.shout', index=9,
      number=10, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='tick_time_series', full_name='RecordDrinkRequest.tick_time_series', index=10,
      number=11, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=195,
  serialized_end=434,
)


_RECORDTEMPERATUREREQUEST = _descriptor.Descriptor(
  name='RecordTemperatureRequest',
  full_name='RecordTemperatureRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sensor_name', full_name='RecordTemperatureRequest.sensor_name', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='temp_c', full_name='RecordTemperatureRequest.temp_c', index=1,
      number=2, type=2, cpp_type=6, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='record_date', full_name='RecordTemperatureRequest.record_date', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=436,
  serialized_end=520,
)

DESCRIPTOR.message_types_by_name['Meta'] = _META
DESCRIPTOR.message_types_by_name['UserRegistrationRequest'] = _USERREGISTRATIONREQUEST
DESCRIPTOR.message_types_by_name['RecordDrinkRequest'] = _RECORDDRINKREQUEST
DESCRIPTOR.message_types_by_name['RecordTemperatureRequest'] = _RECORDTEMPERATUREREQUEST

class Meta(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _META

  # @@protoc_insertion_point(class_scope:Meta)

class UserRegistrationRequest(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _USERREGISTRATIONREQUEST

  # @@protoc_insertion_point(class_scope:UserRegistrationRequest)

class RecordDrinkRequest(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _RECORDDRINKREQUEST

  # @@protoc_insertion_point(class_scope:RecordDrinkRequest)

class RecordTemperatureRequest(_message.Message):
  __metaclass__ = _reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _RECORDTEMPERATUREREQUEST

  # @@protoc_insertion_point(class_scope:RecordTemperatureRequest)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), '\n\020org.kegbot.proto')
# @@protoc_insertion_point(module_scope)
