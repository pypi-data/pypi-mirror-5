import os
from catsnap.web import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0',
            port=port,
            debug=os.environ.get('CATSNAP_DEBUG', False))
