//
// Copyright Aliaksei Levin (levlam@telegram.org), Arseny Smirnov (arseny30@gmail.com) 2014-2022
//
// Distributed under the Boost Software License, Version 1.0. (See accompanying
// file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
//

// ignore_for_file: camel_case_types, non_constant_identifier_names

// AUTO GENERATED FILE, DO NOT EDIT.
//
// Generated by `package:ffigen`.
import 'dart:ffi' as ffi;
import 'package:ffi/ffi.dart' as pkg_ffi;

/// td_json_client.h File Reference.
class td_json_client {
  /// Holds the symbol lookup function.
  final ffi.Pointer<T> Function<T extends ffi.NativeType>(String symbolName)
      _lookup;

  /// The symbols are looked up in [dynamicLibrary].
  td_json_client(ffi.DynamicLibrary dynamicLibrary)
      : _lookup = dynamicLibrary.lookup;

  /// The symbols are looked up with [lookup].
  td_json_client.fromLookup(
      ffi.Pointer<T> Function<T extends ffi.NativeType>(String symbolName)
          lookup)
      : _lookup = lookup;

  /// Returns an opaque identifier of a new TDLib instance.
  /// The TDLib instance will not send updates until the first request is sent to it.
  /// \return Opaque identifier of a new TDLib instance.
  int td_create_client_id() {
    return _td_create_client_id();
  }

  late final _td_create_client_idPtr =
      _lookup<ffi.NativeFunction<ffi.Int32 Function()>>('td_create_client_id');
  late final _td_create_client_id =
      _td_create_client_idPtr.asFunction<int Function()>();

  /// Sends request to the TDLib client. May be called from any thread.
  /// \param[in] client_id TDLib client identifier.
  /// \param[in] request JSON-serialized null-terminated request to TDLib.
  void td_send(
    int client_id,
    ffi.Pointer<pkg_ffi.Utf8> request,
  ) {
    return _td_send(
      client_id,
      request,
    );
  }

  late final _td_sendPtr = _lookup<
      ffi.NativeFunction<
          ffi.Void Function(ffi.Int32, ffi.Pointer<pkg_ffi.Utf8>)>>('td_send');
  late final _td_send =
      _td_sendPtr.asFunction<void Function(int, ffi.Pointer<pkg_ffi.Utf8>)>();

  /// Receives incoming updates and request responses. Must not be called simultaneously from two different threads.
  /// The returned pointer can be used until the next call to td_receive or td_execute, after which it will be deallocated by TDLib.
  /// \param[in] timeout The maximum number of seconds allowed for this function to wait for new data.
  /// \return JSON-serialized null-terminated incoming update or request response. May be NULL if the timeout expires.
  ffi.Pointer<pkg_ffi.Utf8> td_receive(
    double timeout,
  ) {
    return _td_receive(
      timeout,
    );
  }

  late final _td_receivePtr = _lookup<
          ffi.NativeFunction<ffi.Pointer<pkg_ffi.Utf8> Function(ffi.Double)>>(
      'td_receive');
  late final _td_receive =
      _td_receivePtr.asFunction<ffi.Pointer<pkg_ffi.Utf8> Function(double)>();

  /// Synchronously executes a TDLib request.
  /// A request can be executed synchronously, only if it is documented with "Can be called synchronously".
  /// The returned pointer can be used until the next call to td_receive or td_execute, after which it will be deallocated by TDLib.
  /// \param[in] request JSON-serialized null-terminated request to TDLib.
  /// \return JSON-serialized null-terminated request response.
  ffi.Pointer<pkg_ffi.Utf8> td_execute(
    ffi.Pointer<pkg_ffi.Utf8> request,
  ) {
    return _td_execute(
      request,
    );
  }

  late final _td_executePtr = _lookup<
      ffi.NativeFunction<
          ffi.Pointer<pkg_ffi.Utf8> Function(
              ffi.Pointer<pkg_ffi.Utf8>)>>('td_execute');
  late final _td_execute = _td_executePtr.asFunction<
      ffi.Pointer<pkg_ffi.Utf8> Function(ffi.Pointer<pkg_ffi.Utf8>)>();

  /// Sets the callback that will be called when a message is added to the internal TDLib log.
  /// None of the TDLib methods can be called from the callback.
  /// By default the callback is not set.
  ///
  /// \param[in] max_verbosity_level The maximum verbosity level of messages for which the callback will be called.
  /// \param[in] callback Callback that will be called when a message is added to the internal TDLib log.
  /// Pass nullptr to remove the callback.
  void td_set_log_message_callback(
    int max_verbosity_level,
    td_log_message_callback_ptr callback,
  ) {
    return _td_set_log_message_callback(
      max_verbosity_level,
      callback,
    );
  }

  late final _td_set_log_message_callbackPtr = _lookup<
      ffi.NativeFunction<
          ffi.Void Function(ffi.Int32,
              td_log_message_callback_ptr)>>('td_set_log_message_callback');
  late final _td_set_log_message_callback = _td_set_log_message_callbackPtr
      .asFunction<void Function(int, td_log_message_callback_ptr)>();

  /// Creates a new instance of TDLib.
  /// \return Pointer to the created instance of TDLib.
  ffi.Pointer<ffi.Void> td_json_client_create() {
    return _td_json_client_create();
  }

  late final _td_json_client_createPtr =
      _lookup<ffi.NativeFunction<ffi.Pointer<ffi.Void> Function()>>(
          'td_json_client_create');
  late final _td_json_client_create =
      _td_json_client_createPtr.asFunction<ffi.Pointer<ffi.Void> Function()>();

  /// Sends request to the TDLib client. May be called from any thread.
  /// \param[in] client The client.
  /// \param[in] request JSON-serialized null-terminated request to TDLib.
  void td_json_client_send(
    ffi.Pointer<ffi.Void> client,
    ffi.Pointer<pkg_ffi.Utf8> request,
  ) {
    return _td_json_client_send(
      client,
      request,
    );
  }

  late final _td_json_client_sendPtr = _lookup<
      ffi.NativeFunction<
          ffi.Void Function(ffi.Pointer<ffi.Void>,
              ffi.Pointer<pkg_ffi.Utf8>)>>('td_json_client_send');
  late final _td_json_client_send = _td_json_client_sendPtr.asFunction<
      void Function(ffi.Pointer<ffi.Void>, ffi.Pointer<pkg_ffi.Utf8>)>();

  /// Receives incoming updates and request responses from the TDLib client. May be called from any thread, but
  /// must not be called simultaneously from two different threads.
  /// Returned pointer will be deallocated by TDLib during next call to td_json_client_receive or td_json_client_execute
  /// in the same thread, so it can't be used after that.
  /// \param[in] client The client.
  /// \param[in] timeout The maximum number of seconds allowed for this function to wait for new data.
  /// \return JSON-serialized null-terminated incoming update or request response. May be NULL if the timeout expires.
  ffi.Pointer<pkg_ffi.Utf8> td_json_client_receive(
    ffi.Pointer<ffi.Void> client,
    double timeout,
  ) {
    return _td_json_client_receive(
      client,
      timeout,
    );
  }

  late final _td_json_client_receivePtr = _lookup<
      ffi.NativeFunction<
          ffi.Pointer<pkg_ffi.Utf8> Function(
              ffi.Pointer<ffi.Void>, ffi.Double)>>('td_json_client_receive');
  late final _td_json_client_receive = _td_json_client_receivePtr.asFunction<
      ffi.Pointer<pkg_ffi.Utf8> Function(ffi.Pointer<ffi.Void>, double)>();

  /// Synchronously executes TDLib request. May be called from any thread.
  /// Only a few requests can be executed synchronously.
  /// Returned pointer will be deallocated by TDLib during next call to td_json_client_receive or td_json_client_execute
  /// in the same thread, so it can't be used after that.
  /// \param[in] client The client. Currently ignored for all requests, so NULL can be passed.
  /// \param[in] request JSON-serialized null-terminated request to TDLib.
  /// \return JSON-serialized null-terminated request response.
  ffi.Pointer<pkg_ffi.Utf8> td_json_client_execute(
    ffi.Pointer<ffi.Void> client,
    ffi.Pointer<pkg_ffi.Utf8> request,
  ) {
    return _td_json_client_execute(
      client,
      request,
    );
  }

  late final _td_json_client_executePtr = _lookup<
      ffi.NativeFunction<
          ffi.Pointer<pkg_ffi.Utf8> Function(ffi.Pointer<ffi.Void>,
              ffi.Pointer<pkg_ffi.Utf8>)>>('td_json_client_execute');
  late final _td_json_client_execute = _td_json_client_executePtr.asFunction<
      ffi.Pointer<pkg_ffi.Utf8> Function(
          ffi.Pointer<ffi.Void>, ffi.Pointer<pkg_ffi.Utf8>)>();

  /// Destroys the TDLib client instance. After this is called the client instance must not be used anymore.
  /// \param[in] client The client.
  void td_json_client_destroy(
    ffi.Pointer<ffi.Void> client,
  ) {
    return _td_json_client_destroy(
      client,
    );
  }

  late final _td_json_client_destroyPtr =
      _lookup<ffi.NativeFunction<ffi.Void Function(ffi.Pointer<ffi.Void>)>>(
          'td_json_client_destroy');
  late final _td_json_client_destroy = _td_json_client_destroyPtr
      .asFunction<void Function(ffi.Pointer<ffi.Void>)>();
}

/// A type of callback function that will be called when a message is added to the internal TDLib log.
///
/// \param verbosity_level Log verbosity level with which the message was added from -1 up to 1024.
/// If 0, then TDLib will crash as soon as the callback returns.
/// None of the TDLib methods can be called from the callback.
/// \param message Null-terminated UTF-8-encoded string with the message added to the log.
typedef td_log_message_callback_ptr = ffi.Pointer<
    ffi.NativeFunction<
        ffi.Void Function(ffi.Int32, ffi.Pointer<pkg_ffi.Utf8>)>>;
