from dotenv import load_dotenv
from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    broker: AnyUrl = Field(env="BROKER")
    memcached: str = Field(env="MEMCACHED")

    COMMIT_REF: str = Field(env="COMMIT_REF", default="dev")


load_dotenv()
config = Settings()

if __name__ == "__main__":
    print(config.model_dump())
