from app import create_app
from app.websocket.emit_controller import socketio


app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=3500, debug=True, allow_unsafe_werkzeug=True)
