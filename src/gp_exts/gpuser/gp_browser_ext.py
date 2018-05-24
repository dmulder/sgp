from samba.gpclass import gp_ext, gp_ext_setter, gp_inf_ext
from samba.gp_file_append import ini_file_append
import os, pwd
from subprocess import Popen, PIPE

proxy_enable = True
use_same_proxy = False

user_creds = None

class inf_to_profile(gp_ext_setter):
    def __init__(self, *args):
        global user_creds
        self.creds = user_creds
        super(inf_to_profile, self).__init__(*args)
        self.filename = os.path.join(
            pwd.getpwnam(self.creds.get_principal()).pw_dir,
            '.profile'
        )
        self.profile = ini_file_append(self.filename)

    def int_to_bool(self, val=None):
        return int(val if val else self.val) > 0

    def __proxy_enabled(self, val=None):
        global proxy_enable
        if val:
            proxy_enable = self.int_to_bool(val)
        return proxy_enable

    def __use_same_proxy(self, val=None):
        global use_same_proxy
        if val:
            use_same_proxy = self.int_to_bool(val)
        return use_same_proxy

    def set_proxy_url(self, val):
        if self.__proxy_enabled():
            if self.__use_same_proxy():
                if self.attribute == 'http_proxy':
                    self.__set_key_val_profile('http_proxy', val)
                    self.__set_key_val_profile('https_proxy', val)
                    self.__set_key_val_profile('ftp_proxy', val)
            else:
                self.__set_key_val_profile(self.attribute, val)

    def __set_key_val_profile(self, key, val):
        if key in self.profile.keys():
            old_val = self.profile[key]
        else:
            old_val = None
        self.logger.info('%s was changed from %s to %s in %s' % \
            (key, old_val, val, self.filename))
        if val == None:
            del self.profile[key]
        else:
            self.profile[key] = val
        self.gp_db.store(str(self), key, old_val)

    def set_proxy_options(self, val):
        global proxy_enable, use_same_proxy
        if self.attribute == 'proxy_enable':
            self.__proxy_enabled(self.val)
            if not int(val): # Proxy is disabled
                self.__set_key_val_profile('http_proxy', None)
                self.__set_key_val_profile('https_proxy', None)
                self.__set_key_val_profile('ftp_proxy', None)
        elif self.attribute == 'use_same_proxy':
            self.__use_same_proxy(self.val)
            if val: # Use all the same proxy
                if 'http_proxy' in self.profile.keys() and \
                   self.__proxy_enabled():
                    new_val = self.profile['http_proxy']
                    self.__set_key_val_profile('https_proxy', new_val)
                    self.__set_key_val_profile('ftp_proxy', new_val)

    def mapper(self):
        return { 'http_proxy' : (self.set_proxy_url, self.explicit),
                 'https_proxy' : (self.set_proxy_url, self.explicit),
                 'ftp_proxy' : (self.set_proxy_url, self.explicit),
                 'proxy_enable' : (self.set_proxy_options, self.explicit),
                 'use_same_proxy' : (self.set_proxy_options, self.explicit),
               }

    def __str__(self):
        return 'Proxy'

class gp_browser_ext(gp_inf_ext):

    def process_group_policy(self, deleted_gpo_list, changed_gpo_list):
        global user_creds
        user_creds = self.creds
        apmp = { 'Proxy' : { 'Proxy_Enable' : ('proxy_enable', inf_to_profile),
                             'HTTP_Proxy_Server' : ('http_proxy',
                                                    inf_to_profile),
                             'Secure_Proxy_Server' : ('https_proxy',
                                                      inf_to_profile),
                             'FTP_Proxy_Server' : ('ftp_proxy',
                                                   inf_to_profile),
                             'Use_Same_Proxy' : ('use_same_proxy',
                                                 inf_to_profile),
                           },
               }
        inf_file = 'USER/MICROSOFT/IEAK/install.ins'
        for gpo in deleted_gpo_list:
            self.gp_db.set_guid(gpo[0])
            for section in gpo[1].keys():
                current_section = apmp.get(section)
                if not current_section:
                    continue
                for key, value in gpo[1][section].items():
                    setter = None
                    for _, tup in current_section.items():
                        if tup[0] == key:
                            setter = tup[1]
                    if setter:
                        value = value.encode('ascii', 'ignore')
                        setter(self.logger, self.gp_db, self.lp, key,
                               value).delete()
                        self.gp_db.delete(section, key)
                        self.gp_db.commit()

        for gpo in changed_gpo_list:
            if gpo.file_sys_path:
                self.gp_db.set_guid(gpo.name)
                path = gpo.file_sys_path.split('\\sysvol\\')[-1]
                inf_conf = self.parse(os.path.join(path, inf_file))
                if not inf_conf:
                    continue
                for section in inf_conf.sections():
                    current_section = apmp.get(section)
                    if not current_section:
                        continue
                    for key, value in inf_conf.items(section):
                        if current_section.get(key):
                            (att, setter) = current_section.get(key)
                            value = value.encode('ascii', 'ignore')
                            setter(self.logger, self.gp_db, self.lp, att,
                                   value).update_samba()
                            self.gp_db.commit()

    def __str__(self):
        return 'Browser GPO extension'

if __name__ == "__main__":
    from samba import gpo
    import optparse
    from samba import getopt as options
    guid = '{BADA9F20-A366-41C7-A491-00F5AA18F790}'
    name = 'gp_browser_ext'
    path = os.path.abspath(__file__)

    parser = optparse.OptionParser('%s [options]' % name)
    sambaopts = options.SambaOptions(parser)
    parser.add_option_group(sambaopts)

    (opts, args) = parser.parse_args()
    lp = sambaopts.get_loadparm()

    gpo.register_gp_extension(guid, name, path, smb_conf=lp.configfile,
                              machine=False, user=True)

