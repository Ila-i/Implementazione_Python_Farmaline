from sqlalchemy import create_engine

DB_PATH = "DataBase_farmaline.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
connection = engine.connect()
