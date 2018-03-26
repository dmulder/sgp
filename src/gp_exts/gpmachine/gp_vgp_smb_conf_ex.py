import os.path, re
from samba.gpclass import gp_ext, file_to
import xml.etree.ElementTree as etree
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

smb_conf = '/etc/samba/smb.conf'

class SMBConfigParser(ConfigParser):
    def _read(self, fp, fpname):
        cursect = None
        sectname = None
        optname = None
        e = None
        _SECT_TMPL = r"""\[(?P<header>[^]]+)\]"""
        _OPT_TMPL = r"""\s*(?P<option>.*?)\s*(?P<vi>=)\s*(?P<value>.*)$"""
        for lineno, line in enumerate(fp, start=1):
            if not line.strip() or line.strip()[0] == '#':
                continue
            if '#' in line:
                line = line.split('#')[0]
            mo = re.match(_SECT_TMPL, line)
            if mo:
                sectname = mo.group('header')
                if sectname in self._sections:
                    raise DuplicateSectionError(sectname, fpname, lineno)
                else:
                    cursect = self._dict()
                    cursect['__name__'] = sectname
                    self._sections[sectname] = cursect
                optname = None
            elif cursect is None:
                raise MissingSectionHeaderError(fpname, lineno, line)
            else:
                mo = re.match(_OPT_TMPL, line)
                if mo:
                    optname, vi, optval = mo.group('option', 'vi', 'value')
                    cursect[optname] = [optval.strip()]
                else:
                    e = self._handle_error(e, fpname, lineno, line)
        if e:
            raise e
        all_sections = [self._defaults]
        all_sections.extend(self._sections.values())
        for options in all_sections:
            for name, val in options.items():
                if isinstance(val, list):
                    options[name] = '\n'.join(val)

class smb_conf_setter(file_to):
    def set_smb_conf(self, val):
        global smb_conf
        conf = SMBConfigParser()
        conf.read(smb_conf)
        sep = self.attribute.index(':')
        section = self.attribute[:sep]
        option = self.attribute[sep+1:]
        if section not in conf.sections():
            conf.add_section(section)

        if conf.has_option(section, option):
            old_val = conf.get(section, option)
        else:
            old_val = None
        if val is not None:
            conf.set(section, option, val)
        elif val is None and conf.has_option(section, option):
            conf.remove_option(section, option)
        of = open(smb_conf, 'w')
        conf.write(of)
        of.close()
        self.logger.info('smb.conf [%s] %s was changed from %s to %s' % (section, option, old_val, val))

        self.gp_db.store(str(self), self.attribute, old_val)

    def mapper(self):
        return self

    def __getitem__(self, key):
        return (self.set_smb_conf, self.explicit)

    def __str__(self):
        return "smb.conf"

class smb_conf_apply_map:
    def __getitem__(self, key):
        return (key, smb_conf_setter)

    def __contains__(self, key):
        return True

    def get(self, key):
        return (key, smb_conf_setter)

class gp_vgp_smb_conf_ex(gp_ext):
    def __str__(self):
        return "VGP Samba smb.conf Extension"

    def read(self, policy):
        global smb_conf
        self.xml_conf = etree.fromstring(policy)
        apply_map = self.apply_map()['smb.conf']
        ret = False

        sections = self.xml_conf.find('policysetting').find('data').find('configfile').findall('configsection')
        for section_conf in sections:
            section_name = section_conf.find('sectionname').text
            if section_name == 'Configuration File Path':
                smb_conf = section_conf.find('keyvaluepair').find('value').text
                continue
            for option in section_conf.findall('keyvaluepair'):
                key = '%s:%s' % (section_name, section_conf.find('keyvaluepair').find('key').text)
                value = section_conf.find('keyvaluepair').find('value').text
                (att, setter) = apply_map.get(key)
                ret = True
                setter(self.logger,
                       self.ldb,
                       self.gp_db,
                       self.lp,
                       att,
                       value).update_samba()
                self.gp_db.commit()
        return ret


    def list(self, rootpath):
        return os.path.join(rootpath,
            'MACHINE/VGP/VTLA/Samba/SmbConfiguration/manifest.xml')

    def apply_map(self):
        return { 'smb.conf' : smb_conf_apply_map() }

