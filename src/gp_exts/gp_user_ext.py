from samba.gpclass import gp_ext

class gp_user_ext(gp_ext):
    def __init__(self, logger, creds):
        super(gp_ext, self).__init__(logger)
        self.creds = creds
