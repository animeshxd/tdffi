// ignore_for_file: non_constant_identifier_names

import 'dart:ffi';

import 'package:tdffi/tdffi.dart' as td;

void main(List<String> arguments) async {
  var tdlib = td.Bridge(DynamicLibrary.open('native/libtdjson.so.1.8.4'));

  var r =
      await tdlib.td_execute_(td.setLogVerbosityLevel(new_verbosity_level: 0));
  print(r);

  var client_id = tdlib.td_json_client_create();

  var params = td.tdlibParameters(
      database_directory: '/tmp/tdlib',
      use_message_database: true,
      use_secret_chats: true,
      api_id: 94575,
      api_hash: 'a3406de8d171bb422bb6ddf3bbd800e2',
      system_language_code: 'en',
      device_model: 'Desktop',
      application_version: '1.0',
      enable_storage_optimizer: true);

  // tdlib.td_send_(c_id, setTdlibParameters(parameters: params, extra: 1234));
  tdlib.td_json_client_send(client_id, td.getAuthorizationState().toCharPtr());

  while (true) {
    r = await tdlib.td_json_client_receive_(client_id);
    if (r != null) {
      switch (r['@type']) {
        case 'updateAuthorizationState':
          switch (r['authorization_state']['@type']) {
            case 'authorizationStateWaitTdlibParameters':
              tdlib.td_json_client_send(client_id,
                  td.setTdlibParameters(parameters: params).toCharPtr());
              break;
            case 'authorizationStateWaitEncryptionKey':
              var request =
                  td.checkDatabaseEncryptionKey(encryption_key: "").toCharPtr();
              tdlib.td_json_client_send(client_id, request);
              break;
            case 'authorizationStateWaitPhoneNumber':
              tdlib.td_json_client_send(
                client_id,
                td
                    .checkAuthenticationBotToken(
                      token: 'tkn',
                    )
                    .toCharPtr(),
              );
              break;
            case 'authorizationStateReady':
              print('logged in');
              break;
            default:
              print(r);
          }
          break;
        case 'updateConnectionState':
          switch (r['state']['@type']) {
            case 'connectionStateConnecting':
              print('Connecting...');
              break;
            case 'connectionStateReady':
              print('connected');
              break;
            default:
              print(r);
              break;
          }
          break;
        case 'updateOption':
          break;
        case 'error':
          print(r);
          break;
        default:
          print(r);
      }
    }
  }
  tdlib.td_json_client_destroy(client_id);
}
