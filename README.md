PushNotify
==========

Linux has no native Pushbullet client, only a Chromium addon, so here's one to connect Pushbullet to freedesktop.org's Notification specification.

Also attached is a systemd unit file describing this as a user service.
You can install it in ~/.config/systemd/user/pushnotify.service and then run systemctl --user start pushnotify.service .

It's MIT licensed.
