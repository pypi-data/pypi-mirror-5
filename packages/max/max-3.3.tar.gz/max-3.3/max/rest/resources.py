PUBLIC_RESOURCES = {
    'users': {'route': '/people'},
    'user': {'route': '/people/{username}'},
    'avatar': {'route': '/people/{username}/avatar'},
    'user_activities': {'route': '/people/{username}/activities'},

    'activities': {'route': '/activities'},
    'comments': {'route': '/activities/comments'},
    'activity': {'route': '/activities/{activity}'},
    'timeline': {'route': '/people/{username}/timeline'},
    'timeline_authors': {'route': '/people/{username}/timeline/authors'},

    'activity_comments': {'route': '/activities/{activity}/comments'},

    'subscriptions': {'route': '/people/{username}/subscriptions'},
    'subscription': {'route': '/people/{username}/subscriptions/{hash}'},

    'user_conversations': {'route': '/people/{username}/conversations'},
    'user_conversation': {'route': '/people/{username}/conversations/{id}'},

    'contexts': {'route': '/contexts'},
    'context': {'route': '/contexts/{hash}'},
    'context_avatar': {'route': '/contexts/{hash}/avatar'},
    'public_contexts': {'route': '/contexts/public'},
    'context_user_permission': {'route': '/contexts/{hash}/permissions/{username}/{permission}'},
    'context_activities': {'route': '/contexts/{hash}/activities'},
    'context_activities_authors': {'route': '/contexts/{hash}/activities/authors'},

    # MAX 3.0
    'conversations': {'route': '/conversations'},
    'conversation': {'route': '/conversations/{id}'},
    'messages': {'route': '/conversations/{id}/messages'},
    'message': {'route': '/conversations/{id}/messages/{activity}'},
    'participants': {'route': '/conversations/{id}/participants'},
    'participant': {'route': '/conversations/{id}/participant'},

    # MAX 4.0
    'user_shares': {'route': '/people/{username}/shares'},
    'user_likes': {'route': '/people/{username}/likes'},
    'follows': {'route': '/people/{username}/follows'},
    'follow': {'route': '/people/{username}/follows/{followedUsername}'},
    'likes': {'route': '/activities/{activity}/likes'},
    'like': {'route': '/activities/{activity}/likes/{likeId}'},
    'shares': {'route': '/activities/{activity}/shares'},
    'share': {'route': '/activities/{activity}/shares/{shareId}'},

    # Not implemented / Not in roadmap
    'user_comments': {'route': '/people/{username}/comments'},
    'user_conversations': {'route': '/people/{username}/conversations'},
    'comment': {'route': '/activities/{activity}/comments/{commentId}'},
    'context_permissions': {'route': '/contexts/{hash}/permissions'},
    'context_user_permissions': {'route': '/contexts/{hash}/permissions/{username}'},

}

RESTRICTED_RESOURCES = {

    'admin_security': {'route': '/admin/security'},
}

RESOURCES = {}
RESOURCES.update(PUBLIC_RESOURCES)
RESOURCES.update(RESTRICTED_RESOURCES)
