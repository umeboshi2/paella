from useless.db.lowlevel import OperationalError

from tables import packages_columns

def convert_package_data(packagedict, section='main'):
    pcolumns = packages_columns()
    newdict = {}.fromkeys([col.name for col in pcolumns])
    for f in ['package', 'priority', 'filename', 'md5sum',
              'version', 'description', 'size', 'maintainer']:
        try:
            #newdict[f] = packagedict[f].encode('utf-8', 'ignore')
            # decode to utf-8 ignoring errors seems to work here
            # then re-encode to utf-8
            # not sure if any information is lost here, I probably couln't
            # read it anyway.
            newdict[f] = packagedict[f].decode('utf-8', 'ignore').encode('utf-8')
        except KeyError:
            newdict[f] = 'Not Applicable'
    newdict['installedsize'] = packagedict['installed-size']
    if section != 'main':
        newdict['section'] = '/'.join(section, packagedict['section'])
    else:
        newdict['section'] = packagedict['section']
    return newdict

def insert_packages(conn, table, packages, extra={}):
    cursor = conn.cursor(statement=True)
    duplicates = []
    for package in packages:
        try:
            data = convert_package_data(package)
            data.update(extra)
            cursor.insert(table, data=data)
        except OperationalError, inst:
            if inst.args[0].startswith('ERROR:  duplicate key violates unique constraint'):
                duplicates.append(package['package'])
                pass
            else:
                print 'OperationalError occured:',
                print 'number of arguements', len(inst.args)
                count = 1
                for arg in inst.args:
                    print 'arg%d' % count, arg
                raise inst
    return duplicates
