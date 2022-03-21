import copy

import digi
from digi import util

from aws import *

mqtt_connection = None
args = None


@digi.on.obs
def do_obs(sv):
    # TBD update message every second
    if mqtt_connection is not None:
        data = copy.deepcopy(sv)
        data["ts"] = util.get_ts()
        message_json = json.dumps(data)
        mqtt_connection.publish(
            topic=args["topic"],
            payload=message_json,
            qos=mqtt.QoS.AT_LEAST_ONCE)
        digi.logger.info(f"publish {message_json}")


@digi.on.meta
def do_meta(model):
    global mqtt_connection, args

    event_loop_group = io.EventLoopGroup(1)
    host_resolver = io.DefaultHostResolver(event_loop_group)
    client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)

    args = {
        "endpoint": util.get(model, "meta.endpoint"),
        "port": util.get(model, "meta.port"),
        "cert": "certificate.pem.crt",
        "key": "private.pem.key",
        "root_ca": "rootca.pem",
        "client-id": "test-" + str(uuid4()),
        "topic": f"digi/phone",
    }

    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=args["endpoint"],
        port=args["port"],
        cert_filepath=args["cert"],
        pri_key_filepath=args["key"],
        client_bootstrap=client_bootstrap,
        ca_filepath=args["root_ca"],
        on_connection_interrupted=on_connection_interrupted,
        on_connection_resumed=on_connection_resumed,
        client_id=args["client-id"],
        clean_session=False,
        keep_alive_secs=30,
        http_proxy_options=None)

    digi.logger.info("Connecting to {} with client ID '{}'...".format(
        args["endpoint"], args["client-id"]))

    connect_future = mqtt_connection.connect()

    # Future.result() waits until a result is available
    connect_future.result()
    digi.logger.info("Connected!")

    # print("Disconnecting...")
    # disconnect_future = mqtt_connection.disconnect()
    # disconnect_future.result()
    # print("Disconnected!")


if __name__ == '__main__':
    digi.run()
