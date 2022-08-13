// ignore_for_file: non_constant_identifier_names, camel_case_types, unused_element

import 'dart:convert';
import 'dart:ffi';
import 'dart:io';
import 'package:ffi/ffi.dart';

import 'package:tdffi/ffi/td_json_client.dart';
// import 'package:tdffi/td/classes.dart';

import 'package:tdffi/td/functions.dart' show Func;

class Bridge extends td_json_client {
  Bridge._(super.dynamicLibrary);
  Bridge(DynamicLibrary dynamicLibrary) : super(dynamicLibrary);

  static Bridge? _inst;
  static Bridge get tdlib => _inst ??= Bridge._(DynamicLibrary.process());
  static void initilize() {
    if (Platform.isAndroid) {
      DynamicLibrary.open("libtdjson.so");
    } else if (Platform.isLinux) {
      DynamicLibrary.process();
    }
  }

  Future<Map?> td_execute_(Func request) async {
    var c_str = json.encode(request).toNativeUtf8();
    var c = td_execute(c_str);
    malloc.free(c_str);
    if (c == nullptr) {
      return null;
    }

    return c == nullptr ? null : json.decode(c.toDartString());
  }

  void td_send_(int client_id, Func request) async {
    var c_str = json.encode(request).toNativeUtf8();
    td_send(client_id, c_str);
    malloc.free(c_str);
  }

  int td_create_client_id_() {
    return td_create_client_id();
  }

  Future<Map?> td_receive_({double timeout = 10}) async {
    var c = td_receive(timeout);
    return c == nullptr ? null : json.decode(c.toDartString());
  }

  Future<Map?> td_json_client_receive_(Pointer<Void> client, {double timeout = 10}) async {
    var c = td_json_client_receive(client, timeout);
    return c == nullptr ? null : json.decode(c.toDartString());
  }
}
