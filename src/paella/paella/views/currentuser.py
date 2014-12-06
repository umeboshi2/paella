import os
from ConfigParser import ConfigParser
from datetime import datetime

from cornice.resource import resource, view
from trumpet.views.base import BaseUserView

from trumpet.models.usergroup import User

APIROOT = '/rest/v0'

rscroot = os.path.join(APIROOT, 'main')

current_user = os.path.join(rscroot, 'current/user')

def convert_range_to_datetime(start, end):
    "start and end are timestamps"
    start = datetime.fromtimestamp(float(start))
    end = datetime.fromtimestamp(float(end))
    return start, end
    

@resource(path=current_user)
class CurrentUserResource(BaseUserView):
    dbmodel = None
    usermodel = User
    def get(self):
        user = self.get_current_user()
        if user is None:
            data = None
        else:
            data = user.serialize()
            data['groups'] = [g.serialize() for g in user.groups]
            data['config'] = None
            if user.config is not None:
                c = dict()
                config = user.config.get_config()
                for section in config.sections():
                    c[section] = dict()
                    for option in config.options(section):
                        c[section][option] = config.get(section, option)
                data['config'] = c
            else:
                import transaction
                with transaction.manager:
                    user.config.set_config('')
        return data
    
    
    def put(self):
        user = self.get_current_user()
        if user is None:
            raise RuntimeError
        config = self.request.json['config']
        c = ConfigParser()
        for section in config:
            c.add_section(section)
            for option in config[section]:
                c.add_option(option)
                c.set(section, option, config[section][option])
        user.set_config(c)


