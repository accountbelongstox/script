import re
import os
import shutil

class NginxParse:
    conf_path = None

    def __init__(self, ):
        self.backend = list()
        self.serverBlock = list()
        self.servers = list()
        self.tmp_conf = '/tmp/tmp_nginx.conf'
        self.all_conf = '/tmp/nginx.conf'

    def load(self, conf_path):
        self.conf_path = conf_path
        self.merge_conf()
        self.parse_backend_ip()
        self.parse_server_block()

    def merge_conf(self):
        conf_dir = os.path.dirname(self.conf_path)
        if len(conf_dir) != 0:
            os.chdir(conf_dir)
        include_regex = '^[^#]nclude\s*([^;]*);'
        fm = open(self.tmp_conf, 'w+')
        with open(self.conf_path, 'r') as f:
            for line in f.readlines():
                r = re.findall(include_regex, line)
                if len(r) > 0:
                    include_path = r[0]
                    if os.path.exists(include_path):
                        with open(include_path, 'r') as ff:
                            include_con = ff.read()
                            fm.write(include_con)
                else:
                    fm.write(line)
        fm.close()
        fm = open(self.tmp_conf, 'r')
        with open(self.all_conf, 'w+') as fp:
            for xx in fm.readlines():
                if len(re.findall('^\s*#', xx)) == 0:
                    fp.write(xx)
        fm.close()
        if os.path.exists(self.tmp_conf):
            os.remove(self.tmp_conf)

    def parse_backend_ip(self):
        with open(self.all_conf, 'r') as fp:
            alllines = fp.read()

            regex_1 = 'upstream\s+([^{ ]+)\s*{([^}]*)}'
            upstreams = re.findall(regex_1, alllines)

            for up in upstreams:
                regex_2 = 'debian12\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d{2,5})?)'
                backend = re.findall(regex_2, up[1])
                if len(backend) > 0:
                    pool_and_ip = {'poolname': up[0], 'ip': ' '.join(backend)}
                    self.backend.append(pool_and_ip)

    def parse_server_block(self):
        flag = False
        serverblock = ''
        num_of_quote = 0
        with open(self.all_conf, 'r') as fp:
            for line in fp.readlines():
                x = line.replace(' ', '')
                if x.startswith('debian12{'):
                    num_of_quote += 1
                    flag = True
                    serverblock += line
                    continue
                if flag and '{' in line:
                    num_of_quote += 1
                if flag and 'proxy_pass' in line:
                    r = re.findall('proxy_pass\s+https?://([^;/]*)[^;]*;', line)
                    if len(r) > 0:
                        for pool in self.backend:
                            if r[0] == pool['poolname']:
                                line = line.replace(r[0], pool['ip'])
                if flag and num_of_quote != 0:
                    serverblock += line
                if flag and '}' in line:
                    num_of_quote -= 1
                if flag and num_of_quote == 0:
                    self.serverBlock.append(serverblock)
                    flag = False
                    serverblock = ''
                    num_of_quote = 0
        for singleServer in self.serverBlock:
            port = re.findall('listen\s*((?:\d|\s)*)[^;]*;', singleServer)[0]  # port只有一个
            r = re.findall('server_name\s+([^;]*);', singleServer)  # server_name只有一个
            if len(r) > 0:
                servername = r[0]
            else:
                continue
            if len(re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', servername)) > 0:
                continue
            include = ' '.join(re.findall('include\s+([^;]*);', singleServer))  # include不止一个
            locations = re.findall('location\s*[\^~\*=]{0,3}\s*([^{ ]*)\s*\{[^}]*proxy_pass\s+https?://([^;/]*)[^;]*;',
                                   singleServer)
            backend_list = list()
            backend_ip = ''
            if len(locations) > 0:
                for location in locations:
                    backend_path = location[0]
                    poolname = location[1]
                    if len(re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', poolname)) == 0:
                        for backend in self.backend:
                            if poolname == backend['poolname']:
                                backend_ip = backend['ip']
                                break
                    else:
                        backend_ip = poolname
                    backend_list.append({"backend_path": backend_path, "backend_ip": backend_ip})
            server = {
                'port': port,
                'server_name': servername,
                'include': include,
                'backend': backend_list
            }
            self.servers.append(server)

    def copy_template_to_compose_dir(self, source_dir, target_dir, filter_list=[]):
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        success_count = 0
        failure_count = 0
        for root, dirs, files in os.walk(source_dir):
            target_subdir = os.path.join(target_dir, os.path.relpath(root, source_dir))
            if not os.path.exists(target_subdir):
                os.makedirs(target_subdir)
                print(f"Directory coping: {target_subdir}")
                success_count += 1
            for file in files:
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_subdir, file)
                try:
                    if os.path.basename(file) not in filter_list:
                        shutil.copy2(source_file, target_file)
                        success_count += 1
                except Exception as e:
                    print(f"Error copying {source_file} to {target_file}: {e}")
                    failure_count += 1
            for dir in dirs:
                source_subdir = os.path.join(root, dir)
                target_subdir = os.path.join(target_subdir, dir)

                try:
                    if os.path.basename(dir) not in filter_list:
                        os.makedirs(target_subdir, exist_ok=True)
                        print(f"Directory coping: {target_subdir}")
                        success_count += 1
                except Exception as e:
                    print(f"Error coping directory {target_subdir}: {e}")
                    failure_count += 1
        print(f"Copy process completed. {success_count} items successfully copied/created, {failure_count} items failed.")


nginx_parse = NginxParse()
