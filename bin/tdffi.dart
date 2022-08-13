// ignore_for_file: non_constant_identifier_names

import 'dart:ffi';

import 'package:tdffi/tdffi.dart' as tdffi;
import 'package:tdffi/tdffi.dart';

void main(List<String> arguments) async {
    var tdlib = tdffi.Bridge(DynamicLibrary.open('native/libtdjson.so.1.8.4'));
  
  var r = await tdlib.td_execute_(setLogVerbosityLevel());
  print(r);

  var client_id = tdlib.td_create_client_id();

  var params = tdlibParameters(
          database_directory: '/tmp/tdlib',
          use_message_database: true,
          use_secret_chats: true,
          api_id: 94575,
          api_hash: 'a3406de8d171bb422bb6ddf3bbd800e2',
          system_language_code: 'en',
          device_model: 'Desktop',
          application_version: '1.0',
          enable_storage_optimizer: true)
      ;

  // tdlib.td_send_(c_id, setTdlibParameters(parameters: params, extra: 1234));
  tdlib.td_send(client_id, setTdlibParameters(parameters: params).toCharPtr());

  while (true) {
    r = await tdlib.td_receive_();
    if (r != null) {
      print(r['@type']);
      print(r);
    }
  }
}
