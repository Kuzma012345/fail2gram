import datetime


def format_get_event(list_events: list) -> str:
    res = ''

    for event in list_events:
        if len(event) == 3:
            event_occurrence_time, event_kind, tracked_remote_ip = event

            event_occurrence_time = event_occurrence_time.isoformat()

            res += f'''📌{event_occurrence_time=}, 
📌{event_kind=}, 
📌{tracked_remote_ip=}
\n'''

    return res


def format_get_ban(list_bans: list) -> str:
    res = ''

    for event in list_bans:
        if len(event) == 3:
            ban_begin_time, ban_duration, tracked_remote_ip = event

            ban_begin_time = ban_begin_time.isoformat()
            ban_duration = ':'.join(str(ban_duration).split(':')[:2])

            res += f'''📌{ban_begin_time=}, 
📌{ban_duration=}, 
📌{tracked_remote_ip=}
\n'''

    return res


def format_get_remote_connection(list_remote_connections: list) -> str:
    res = ''

    for event in list_remote_connections:
        if len(event) == 3:
            first_observation_time, last_observation_time, tracked_remote_ip = event

            last_observation_time = last_observation_time.isoformat()
            first_observation_time = first_observation_time.isoformat()

            res += f'''📌{first_observation_time=}, 
📌{last_observation_time=}, 
📌{tracked_remote_ip=}
\n'''

    return res
