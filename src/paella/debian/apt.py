
class Foo:
    pass

if __name__ == '__main__':
    import apt_pkg as Apt
    Apt.init()
    c = Apt.GetCache()
    print c.Packages
    
