django-notifier
===============

Send notifications (Email, SMS etc) and manage preferences and permissions per user and group.


To register a notification:
create_notification('test-notification')

To send notifications:
send_notification('test-notification', [user1, user2, ..])
