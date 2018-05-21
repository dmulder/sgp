from samba.gpclass import gp_ext, gp_ext_setter
from gp_exts.gp_file_append import ini_file_append
import xml.etree.ElementTree as etree
import re, os, os.path

sysconfdir = '/etc'

class gp_environment_variable_ext(gp_ext):

    def set_env_var(self, attribute, val):
        global sysconfdir
        if type(val) is not dict:
            val = { 'value': val, 'action': 'U' }

        # MS PATH variable is seperated by ';', which if placed in a posix
        # PATH causes everything after the ';' to be executed, which is not
        # what we intend. So, ignore PATH variables that contain ';'. Also
        # ensure the first character in the PATH is something valid (rather
        # than C:\ or something).
        if val['value'] and attribute == 'PATH' and \
           (';' in val['value'] or \
           val['value'][0] not in ['/', '$', '~', '.']):
            self.logger.info('Ignored PATH variable assignment due to it\'s' +\
                ' similarity to a Windows PATH: %s' % val['value'])
            return

        profile = ini_file_append(os.path.join(sysconfdir, 'profile'))

        old_val = profile[attribute]
        self.logger.info('Environment Variable %s was changed from %s to %s' \
                         % (attribute, old_val, val['value']))

        if val['value'] == None:
            del profile[attribute]
        # Update, Replace, and Create all really do the same thing
        elif val['action'] == 'U' or \
             val['action'] == 'R' or \
             val['action'] == 'C':
            if attribute == 'PATH' and \
               'partial' in val and \
               val['partial'] == '1':
                profile[attribute] = '$PATH:%s' % val['value']
            else:
                profile[attribute] = val['value']
        # Remove should blank the variable
        elif val['action'] == 'D':
            profile[attribute] = ''

        self.gp_db.store(str(self), attribute, old_val)

    def read(self, policy):
        return etree.fromstring(policy)

    def process_group_policy(self, deleted_gpo_list, changed_gpo_list):
        xml_file = \
            'MACHINE/Preferences/EnvironmentVariables/EnvironmentVariables.xml'
        for gpo in deleted_gpo_list:
            self.gp_db.set_guid(gpo[0])
            for section in gpo[1].keys():
                for key, value in gpo[1][section].items():
                    self.set_env_var(key, value)
                    self.gp_db.commit()

        for gpo in changed_gpo_list:
            if gpo.file_sys_path:
                self.gp_db.set_guid(gpo.name)
                path = gpo.file_sys_path.split('\\sysvol\\')[-1]
                xml_conf = self.parse(os.path.join(path, xml_file))
                if not xml_conf:
                    continue

                for env_var in xml_conf.findall('EnvironmentVariable'):
                    att = env_var.attrib['name']
                    self.set_env_var(att, env_var.find('Properties').attrib)
                    self.gp_db.commit()

    def __str__(self):
        return 'Environment GPO extension'

