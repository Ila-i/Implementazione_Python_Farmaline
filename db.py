from sqlalchemy import create_engine
# collegamento al database della farmacia
DB_PATH = "DataBase_farmaline.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
connection = engine.connect()
