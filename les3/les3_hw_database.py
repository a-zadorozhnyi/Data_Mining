from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from les3_hw_models import Base, Post, Writer


class HabrDB:

    def __init__(self, db_link):
        engine = create_engine(db_link)
        Base.metadata.create_all(engine)
        self.session_db = sessionmaker(bind=engine)

    def get_session(self) -> Session:
        return self.__session_db()

    @staticmethod
    def get_or_update(session, model):
        try:
            session.add(model)
            session.commit()
        except Exception as _:
            session.rollback()
            model = session.query(type(model)).filter(type(model).url == model.url).first()
        return model

    def add_post(self, post_obj):
        session = self.get_session()
        post_obj.writer = self.get_or_update(session, post_obj.writer)
        post_obj.tag = [self.get_or_update(session, itm) for itm in post_obj.tag]
        post_obj.hub = [self.get_or_update(session, itm) for itm in post_obj.hub]
        print(post_obj.writer)
        print(post_obj.tag)
        print(post_obj.hub)

        try:
            session.add(post_obj)
            session.commit()
        except Exception as e:
            print(e)
        finally:
            session.close()