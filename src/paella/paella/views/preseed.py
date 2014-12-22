import logging

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.renderers import render


from paella.managers.main import MachineManager
from paella.managers.recipes import PartmanRecipeManager
from paella.managers.recipes import PartmanRaidRecipeManager

log = logging.getLogger(__name__)

def _installer_view(request, template):
    mgr = MachineManager(request.db)
    settings = request.registry.settings
    paella_server_ip = settings['paella_server_ip']
    uuid = request.matchdict['uuid']
    m = mgr.get_by_uuid(uuid)
    name = m.name
    recipe = None
    if m.recipe_id is not None:
        pmgr = PartmanRecipeManager(request.db)
        recipe = pmgr.prepare_recipe(m.recipe_id)
    raid_recipe = None
    disk_list = None
    if m.raid_recipe_id is not None:
        rdmgr = PartmanRaidRecipeManager(request.db)
        # FIXME:  This is a hacky way to generate a disk list
        # for raid configurations.  This hack presumes that the
        # block devices are partitioned and that the block device
        # names don't end in digits, although the partitions may.
        r = rdmgr.get(m.raid_recipe_id)
        lines = r.content.split('\n')
        disklines = [l for l in lines if '/dev/' in l]
        devices = list()
        for dline in disklines:
            dline = dline.strip()
            devlist = dline.split('#')
            for dev in devlist:
                # strip ending digits
                while dev[-1].isdigit():
                    dev = dev[:-1]
                if dev not in devices:
                    devices.append(dev)
        if len(devices):
            # sort the list after info gathering complete
            devices.sort()
            disk_list = devices
        raid_recipe = rdmgr.prepare_recipe(m.raid_recipe_id)
    keydata = mgr.keymanager.get(m.id)
    env = dict(uuid=uuid, hostname=name, machine=name,
               paella_server_ip=paella_server_ip,
               recipe=recipe, raid_recipe=raid_recipe,
               disk_list=disk_list, keydata=keydata,
               masterkey=mgr.keymanager.masterkey)
    content = render(template, env)
    return content
    

@view_config(route_name='preseed',
             renderer='string')
def preseed_view(request):
    template = 'paella:templates/preseed.mako'
    return _installer_view(request, template)

@view_config(route_name='latecmd',
             renderer='string')
def latecmd_view(request):
    template = 'paella:templates/configure-salt-netboot.mako'
    return _installer_view(request, template)
    
