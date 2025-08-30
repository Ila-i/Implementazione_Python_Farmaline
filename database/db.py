from sqlalchemy import create_engine

#Inserire il percorso file dove si trova la base di dati del proprio dispositivo

DB_PATH = "DataBase_farmaline.db"
engine = create_engine(f"sqlite:///{DB_PATH}")
connection = engine.connect()
