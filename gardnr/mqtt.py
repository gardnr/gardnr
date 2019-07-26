#!/usr/bin/env python

from paho.mqtt import subscribe


def main() -> None:
    subscribe.callback(consume_message, 'sensor')


def consume_message(client, userdata, message) -> None:
    print(message.payload)


if __name__ == '__main__':
    main()
