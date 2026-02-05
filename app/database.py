from sqlmodel import SQLModel, create_engine, Session

# Replace with your MySQL credentials
DATABASE_URL = "mysql+pymysql://root:Rahul315%40@localhost:3306/fastapi_task"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True,           # Logs SQL queries
    pool_pre_ping=True   # Avoid connection drops
)

# Dependency for FastAPI
def get_session():
    with Session(engine) as session:
        yield session
