from django.conf import settings 

XMLRPC_DEFAULT_METHODS = (
    ('tapatalk.forum.get_config', 'get_config'),
    ('tapatalk.forum.get_forum', 'get_forum'),
    ('tapatalk.forum.get_online_users', 'get_online_users'),

    ('tapatalk.search.search_topic', 'search_topic'),
    ('tapatalk.search.search_post', 'search_post'),

    ('tapatalk.user.login', 'login'),
    ('tapatalk.user.get_inbox_stat', 'get_inbox_stat'),
    ('tapatalk.user.get_user_info', 'get_user_info'),
    ('tapatalk.user.get_user_topic', 'get_user_topic'),
    ('tapatalk.user.get_user_reply_post', 'get_user_reply_post'),

    ('tapatalk.topic.get_unread_topic', 'get_unread_topic'),
    ('tapatalk.topic.get_participated_topic', 'get_participated_topic'),
    ('tapatalk.topic.get_latest_topic', 'get_latest_topic'),
    ('tapatalk.topic.get_topic', 'get_topic'),
    ('tapatalk.topic.new_topic', 'new_topic'),

    ('tapatalk.post.get_thread', 'get_thread'),
    ('tapatalk.post.reply_post', 'reply_post'),
    ('tapatalk.post.get_raw_post', 'get_raw_post'),
    ('tapatalk.post.save_raw_post', 'save_raw_post'),

    ('tapatalk.subscription.get_subscribed_topic', 'get_subscribed_topic'),

    ('tapatalk.pm.get_box_info', 'get_box_info'),
    ('tapatalk.pm.get_box', 'get_box'),
    ('tapatalk.pm.get_message', 'get_message'),
    ('tapatalk.pm.delete_message', 'delete_message'),
    ('tapatalk.pm.create_message', 'create_message'),
)

try:
    TAPATALK_METHODS = XMLRPC_DEFAULT_METHODS + settings.TAPATALK_METHODS
except:
    TAPATALK_METHODS = XMLRPC_DEFAULT_METHODS
