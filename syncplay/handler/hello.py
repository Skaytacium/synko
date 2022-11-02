def main(user: str, room: str, chat: str):
    return {"Hello": {
        "username": user,
            "room": {"name": room},
            # Version is protocol version
            "version": "1.2.7",
            # Real version is client version
            "realversion": "1.6.9",
            "features": {
                "chat": chat,
                "featureList": "false",
                "readiness": "true",
                "managedRooms": "false"
            },
            "motd": ""
            }}
