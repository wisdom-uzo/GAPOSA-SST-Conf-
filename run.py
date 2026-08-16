import os
from app import create_app
from config import Config

app = create_app(Config)

if __name__ == '__main__':
    port_str = os.environ.get('PORT', '5000')
    port = int(port_str) if port_str and port_str.strip().isdigit() else 5000
    debug = (os.environ.get('FLASK_DEBUG') or 'True').lower() in ('true', '1', 't')
    print(f"[*] Starting ICONFST'26 Conference Web Portal on http://127.0.0.1:{port}")
    app.run(host='0.0.0.0', port=port, debug=debug, use_reloader=False)
