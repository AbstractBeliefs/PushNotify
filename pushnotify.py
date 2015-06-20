import logging
import dbus
import websocket
import json

import config

# Set up logger, DBus, websocket.
logging.basicConfig(level=config.loglevel)
logger = logging.getLogger(__file__)

def ephemeral(response):
    if response["push"]["type"] == "mirror":
        notification_iface.Notify(
            "pushnotify",       # DBus Application Name
            0,                  # Notification-replaces
            "",                 # Icon
            response["push"]["application_name"] + " - " + response["push"]["title"],
            response["push"]["body"],   # Body
            [],                 # Actions
            [],                 # Hints
            -1                  # Timeout
        )
    logger.info("Notified: %s - %s" %(response["push"]["application_name"], response["push"]["title"]))

logger.debug("Connecting to DBus")
bus = dbus.SessionBus()
notification_object = bus.get_object(
    "org.freedesktop.Notifications",
    "/org/freedesktop/Notifications"
)
notification_iface = dbus.Interface(notification_object, "org.freedesktop.Notifications")

logger.debug("Connecting to websocket")
ws = websocket.create_connection("wss://stream.pushbullet.com/websocket/%s" %(config.token))


logger.debug("Beginning main loop")
while True:
    try:
        response = json.loads(ws.recv())
        logger.debug(str(response))
        if response["type"] == "nop":
            logger.debug("Received nop")
            continue

        elif response["type"] == "tickle":
            logger.info("Received a tickle for %s" %(response["subtype"]))
            continue

        elif response["type"] == "push":
            logger.info("Received an ephemeral")
            ephemeral(response)
            continue

        else:
            logger.debug("Received unknown push type")
            continue

    except KeyboardInterrupt:
        logger.debug("Caught KeyboardInterrupt, closing")
        break

    except websocket.WebSocketException:
        logger.warning("Socket exception, trying to reopen")
        try:
            ws = websocket.create_connection("wss://stream.pushbullet.com/websocket/%s" %(config.token))
        except Exception as e:
            logger.exception("Couldn't fix the socket, exiting: %s" %(str(e)))
            break

    except Exception as e:
        logger.exception("Caught unhandled exception: %s" %(str(e)))

logger.debug("Closing websocket")
ws.close()
logger.debug("Done")
