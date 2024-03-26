from pycore.utils import arr, tool
from pycore._base import Base


class ConfigWeights(Base):
    def get_by_extend(self, key, p_config, com_config, lang_map=None):
        configs = p_config.get(key) or []
        by_language = p_config.get('extendByLanguage', {})
        by_framework = p_config.get('extendByFramework', {})
        if lang_map != None:
            languages = [lang_map.get("lang")]
            frameworks = [lang_map.get("frameworks")]
        else:
            languages = p_config.get('language') or com_config.get('language')
            frameworks = p_config.get('framework') or com_config.get('framework')
        language_config = []
        framework_config = []
        for language in languages:
            language = language.lower()
            language_config.extend(by_language.get(language, {}).get(key, []))
        for framework in frameworks:
            framework = framework.lower()
            framework_config.extend(by_framework.get(framework, {}).get(key, []))
        nList = configs + language_config + framework_config
        merged_configs = []
        for item in nList:
            if isinstance(item, str):
                merged_configs = list(set(nList))
            else:
                merged_configs.append(item)
            # else:
            #     self.warn("Configuring read analysis has no implemented support.")
            #     pass
        return merged_configs

    def get_file_filters(self, project_path, p_config, com_config, lang_map=None):
        filter_files = self.get_by_extend('filterFiles', p_config, com_config, lang_map=lang_map)
        return filter_files

    def get_folder_filters(self, project_path, p_config, com_config, lang_map=None):
        filter_folders = self.get_by_extend('filterFolder', p_config, com_config, lang_map=lang_map)
        return filter_folders

    def get_extension_filters(self, project_path, p_config, com_config, lang_map=None):
        extension_filters = self.get_by_extend('filterExtension', p_config, com_config, lang_map=lang_map)
        return extension_filters

    def get_file_start_filters(self, project_path, p_config, com_config, lang_map=None):
        file_start_filters = self.get_by_extend('filterFileStartsWith', p_config, com_config, lang_map=lang_map)
        return file_start_filters

    def get_file_end_filters(self, project_path, p_config, com_config, lang_map=None):
        file_end_filters = self.get_by_extend('filterFileEndsWith', p_config, com_config, lang_map=lang_map)
        return file_end_filters

    def get_folder_start_filters(self, project_path, p_config, com_config, lang_map=None):
        folder_start_filters = self.get_by_extend('filterFolderStartsWith', p_config, com_config, lang_map=lang_map)
        return folder_start_filters

    def get_folder_end_filters(self, project_path, p_config, com_config, lang_map=None):
        folder_end_filters = self.get_by_extend('filterFolderEndsWith', p_config, com_config, lang_map=lang_map)
        return folder_end_filters

    def get_all_filters(self, project_path, p_config, com_config, lang_map=None):
        all_filters = {}
        all_filters['file_filters'] = self.get_by_extend('filterFiles', p_config, com_config, lang_map=lang_map)
        all_filters['extension_filters'] = self.get_by_extend('filterExtension', p_config, com_config,
                                                              lang_map=lang_map)
        all_filters['file_start_filters'] = self.get_by_extend('filterFileStartsWith', p_config, com_config,
                                                               lang_map=lang_map)
        all_filters['file_end_filters'] = self.get_by_extend('filterFileEndsWith', p_config, com_config,
                                                             lang_map=lang_map)
        all_filters['folder_filters'] = self.get_by_extend('filterFolder', p_config, com_config, lang_map=lang_map)
        all_filters['folder_filters'] = self.get_by_extend('filterFolder', p_config, com_config, lang_map=lang_map)
        all_filters['folder_start_filters'] = self.get_by_extend('filterFolderStartsWith', p_config, com_config,
                                                                 lang_map=lang_map)
        all_filters['folder_end_filters'] = self.get_by_extend('filterFolderEndsWith', p_config, com_config,
                                                               lang_map=lang_map)
        return all_filters


config_weights = ConfigWeights()
