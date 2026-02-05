from sqlmodel import SQLModel, create_engine, Session
DATABASE_URL = "mysql+pymysql://root:Rahul315%40@localhost:3306/fastapi_task"

engine = create_engine(
    DATABASE_URL,
    echo=True,           
    pool_pre_ping=True  
)

def get_session():
    with Session(engine) as session:
        yield session

