from .socket_io import sio

# In-memory store for online users
# In a production app, you'd use Redis or a similar store
online_users = {}

@sio.event
async def connect(sid, environ):
    print(f"connect {sid}")

@sio.event
async def disconnect(sid):
    print(f"disconnect {sid}")
    user_id_to_remove = None
    for user_id, user_data in online_users.items():
        if user_data['sid'] == sid:
            user_id_to_remove = user_id
            break
    if user_id_to_remove:
        del online_users[user_id_to_remove]
    await sio.emit('online_users', list(online_users.values()))

@sio.event
async def user_online(sid, data):
    user_id = data.get('userId')
    online_users[user_id] = {
        'id': user_id,
        'sid': sid,
        'username': data.get('username'),
        'elo': data.get('elo')
    }
    await sio.emit('online_users', list(online_users.values()))

@sio.event
async def user_offline(sid, data):
    user_id = data.get('userId')
    if user_id in online_users:
        del online_users[user_id]
    await sio.emit('online_users', list(online_users.values()))

@sio.event
async def challenge_user(sid, data):
    opponent_id = data.get('opponentId')
    challenger = data.get('challenger')
    topic = data.get('topic')

    # Check if opponent_id is a string and exists in online_users
    if isinstance(opponent_id, str) and opponent_id in online_users:
        opponent_sid = online_users[opponent_id]['sid']
        await sio.emit('challenge_received', {'challenger': challenger, 'topic': topic}, room=opponent_sid)
    # Check if opponent_id is an integer and exists in online_users
    elif isinstance(opponent_id, int) and str(opponent_id) in online_users:
        opponent_sid = online_users[str(opponent_id)]['sid']
        await sio.emit('challenge_received', {'challenger': challenger, 'topic': topic}, room=opponent_sid)


@sio.event
async def accept_challenge(sid, data):
    challenger_id = data.get('challengerId')
    opponent = data.get('opponent')
    topic = data.get('topic')

    if isinstance(challenger_id, str) and challenger_id in online_users:
        challenger_sid = online_users[challenger_id]['sid']
        await sio.emit('challenge_accepted', {'opponent': opponent, 'topic': topic}, room=challenger_sid)
    elif isinstance(challenger_id, int) and str(challenger_id) in online_users:
        challenger_sid = online_users[str(challenger_id)]['sid']
        await sio.emit('challenge_accepted', {'opponent': opponent, 'topic': topic}, room=challenger_sid)


@sio.event
async def decline_challenge(sid, data):
    challenger_id = data.get('challengerId')
    if isinstance(challenger_id, str) and challenger_id in online_users:
        challenger_sid = online_users[challenger_id]['sid']
        await sio.emit('challenge_declined', {}, room=challenger_sid)
    elif isinstance(challenger_id, int) and str(challenger_id) in online_users:
        challenger_sid = online_users[str(challenger_id)]['sid']
        await sio.emit('challenge_declined', {}, room=challenger_sid)
