import os
import tempfile
from nautto import create_app, db

if __name__ == '__main__':
    db_fd, db_fname = tempfile.mkstemp()
    config = {
        "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_fname,
        "TESTING": True
    }
    
    app = create_app(config)
    
    with app.app_context():
        db.create_all()

    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000)
    
    os.close(db_fd)
    os.unlink(db_fname)
    