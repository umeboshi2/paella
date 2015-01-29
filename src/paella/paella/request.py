from pyramid.request import Request
from pyramid.decorator import reify
import transaction

class AlchemyRequest(Request):
    @reify
    def db(self):
        maker = self.registry.settings['db.sessionmaker']
        session = maker()
        def close_session(request):
            if request.exception is not None:
                transaction.abort()
            else:
                transaction.commit()
            session.close()
        self.add_finished_callback(close_session)
        return session
    
    @reify
    def usermodel(self):
        usermodel = self.registry.settings['db.usermodel']
        return usermodel
    
    @reify
    def password_model(self):
        password_model = self.registry.settings['db.password_model']
        return password_model
    
