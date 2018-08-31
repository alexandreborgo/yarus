
import subprocess
import os

class Ansible:

	playbooks_dir = '/opt/yarus/tmp/playbooks/'

	def generate_playbook_check_client(self, task_id, client):		
		self.playbook = self.playbooks_dir + task_id + '_' + client.ID + '.yml'
		playbook = open(self.playbook, "w")
		playbook.write("---\n")
		playbook.write("- hosts: " + client.IP + "\n")
		playbook.write("  remote_user: yarus\n")
		playbook.write("  become: true\n")
		playbook.write("  gather_facts: no\n")
		playbook.write("  tasks:\n")
		playbook.write("  - name: check\n")
		playbook.write("    ping:\n")
		playbook.close()
	def generate_playbook_check_group(self, task_id, group, grouped):
		self.playbook = self.playbooks_dir + task_id + '_' + group.ID + '.yml'
		playbook = open(self.playbook, "w")
		playbook.write("---\n")
		playbook.write("- hosts:\n")
		for client in grouped:
			playbook.write("  - " + client['IP'] + "\n")
		playbook.write("  remote_user: yarus\n")
		playbook.write("  become: true\n")
		playbook.write("  gather_facts: no\n")
		playbook.write("  tasks:\n")
		playbook.write("  - name: check\n")
		playbook.write("    ping:\n")		
		playbook.close()

	def generate_playbook_config_client(self, task_id, client, file):
		self.playbook = self.playbooks_dir + task_id + '_' + client.ID + '.yml'
		playbook = open(self.playbook, "w")
		playbook.write("---\n")
		playbook.write("- hosts: " + client.IP + "\n")
		playbook.write("  remote_user: yarus\n")
		playbook.write("  become: true\n")
		playbook.write("  gather_facts: true\n")
		playbook.write("  tasks:\n")
		playbook.write("  - name: config\n")
		playbook.write("    file:\n")
		playbook.write("      state: absent\n")
		playbook.write("      path: /etc/yum.repos.d/\n")
		playbook.write("    when: ansible_distribution == 'CentOS' or ansible_distribution == 'Red Hat Enterprise Linux'\n")			
		playbook.write("  - name: config\n")
		playbook.write("    file:\n")
		playbook.write("      state: directory\n")
		playbook.write("      path: /etc/yum.repos.d/\n")
		playbook.write("    when: ansible_distribution == 'CentOS' or ansible_distribution == 'Red Hat Enterprise Linux'\n")
		playbook.write("  - name: config\n")
		playbook.write("    copy:\n")
		playbook.write("      src: " + file + "\n")
		playbook.write("      dest: /etc/yum.repos.d/\n")
		playbook.write("      owner: root\n")
		playbook.write("      group: root\n")
		playbook.write("    when: ansible_distribution == 'CentOS' or ansible_distribution == 'Red Hat Enterprise Linux'\n")
		playbook.write("  - name: config\n")
		playbook.write("    file:\n")
		playbook.write("      state: absent\n")
		playbook.write("      path: /etc/apt/sources.list\n")
		playbook.write("    when: ansible_distribution == 'Debian' or ansible_distribution == 'Ubuntu'\n")
		playbook.write("  - name: config\n")
		playbook.write("    file:\n")
		playbook.write("      state: absent\n")
		playbook.write("      path: /etc/apt/sources.list.d/\n")
		playbook.write("    when: ansible_distribution == 'Debian' or ansible_distribution == 'Ubuntu'\n")
		playbook.write("  - name: config\n")
		playbook.write("    copy:\n")
		playbook.write("      src: " + file + "\n")
		playbook.write("      dest: /etc/apt/sources.list\n")
		playbook.write("      owner: root\n")
		playbook.write("      group: root\n")
		playbook.write("    when: ansible_distribution == 'Debian' or ansible_distribution == 'Ubuntu'\n")
		playbook.close()
	def generate_playbook_config_group(self, task_id, group, client_list):
		self.playbook = self.playbooks_dir + task_id + '_' + group.ID + '.yml'
		playbook = open(self.playbook, "w")
		playbook.write("---\n")		
		playbook.write("- hosts:\n")
		for client in client_list:
			playbook.write("  - " + client['client'].IP + "\n")
		playbook.write("  remote_user: yarus\n")
		playbook.write("  become: true\n")
		playbook.write("  gather_facts: true\n")
		playbook.write("  tasks:\n")
		playbook.write("  - name: config\n")
		playbook.write("    file:\n")
		playbook.write("      state: absent\n")
		playbook.write("      path: /etc/yum.repos.d/\n")
		playbook.write("    when: ansible_distribution == 'CentOS' or ansible_distribution == 'Red Hat Enterprise Linux'\n")			
		playbook.write("  - name: config\n")
		playbook.write("    file:\n")
		playbook.write("      state: directory\n")
		playbook.write("      path: /etc/yum.repos.d/\n")
		playbook.write("    when: ansible_distribution == 'CentOS' or ansible_distribution == 'Red Hat Enterprise Linux'\n")
		playbook.write("  - name: config\n")
		playbook.write("    copy:\n")
		playbook.write("      src: /opt/yarus/tmp/yarus_{{ inventory_hostname }}.repo\n")
		playbook.write("      dest: /etc/yum.repos.d/\n")
		playbook.write("      owner: root\n")
		playbook.write("      group: root\n")
		playbook.write("    when: ansible_distribution == 'CentOS' or ansible_distribution == 'Red Hat Enterprise Linux'\n")
		playbook.write("  - name: config\n")
		playbook.write("    file:\n")
		playbook.write("      state: absent\n")
		playbook.write("      path: /etc/apt/sources.list\n")
		playbook.write("    when: ansible_distribution == 'Debian' or ansible_distribution == 'Ubuntu'\n")
		playbook.write("  - name: config\n")
		playbook.write("    file:\n")
		playbook.write("      state: absent\n")
		playbook.write("      path: /etc/apt/sources.list.d/\n")
		playbook.write("    when: ansible_distribution == 'Debian' or ansible_distribution == 'Ubuntu'\n")
		playbook.write("  - name: config\n")
		playbook.write("    copy:\n")
		playbook.write("      src: /opt/yarus/tmp/sources_{{ inventory_hostname }}.list\n")
		playbook.write("      dest: /etc/apt/sources.list\n")
		playbook.write("      owner: root\n")
		playbook.write("      group: root\n")
		playbook.write("    when: ansible_distribution == 'Debian' or ansible_distribution == 'Ubuntu'\n")
		playbook.close()

	def generate_playbook_upgradable_client(self, task_id, client):
		self.playbook = self.playbooks_dir + task_id + '_' + client.ID + '.yml'
		playbook = open(self.playbook, "w")
		playbook.write("---\n")
		playbook.write("- hosts: " + client.IP + "\n")
		playbook.write("  remote_user: yarus\n")
		playbook.write("  become: true\n")
		playbook.write("  gather_facts: true\n")
		playbook.write("  tasks:\n")
		playbook.write("  - name: prep\n")
		playbook.write("    command: yum repolist\n")
		playbook.write("    when: ansible_distribution == 'CentOS' or ansible_distribution == 'Red Hat Enterprise Linux'\n")
		playbook.write("  - name: prep\n")
		playbook.write("    command: apt update\n")
		playbook.write("    when: ansible_distribution == 'Debian' or ansible_distribution == 'Ubuntu'\n")
		playbook.write("  - name: upgradable\n")
		playbook.write("    command: yum list updates -q\n")
		playbook.write("    when: ansible_distribution == 'CentOS' or ansible_distribution == 'Red Hat Enterprise Linux'\n")
		playbook.write("  - name: upgradable\n")
		playbook.write("    command: apt list --upgradable\n")
		playbook.write("    when: ansible_distribution == 'Debian' or ansible_distribution == 'Ubuntu'\n")
		playbook.close()
	def generate_playbook_upgradable_group(self, task_id, group, groupeds):
		self.playbook = self.playbooks_dir + task_id + '_' + group.ID + '.yml'
		playbook = open(self.playbook, "w")
		playbook.write("---\n")
		playbook.write("- hosts:\n")
		for client in groupeds:
			playbook.write("  - " + client['IP'] + "\n")
		playbook.write("  remote_user: yarus\n")
		playbook.write("  become: true\n")
		playbook.write("  gather_facts: true\n")
		playbook.write("  tasks:\n")
		playbook.write("  - name: prep\n")
		playbook.write("    command: yum repolist\n")
		playbook.write("    when: ansible_distribution == 'CentOS' or ansible_distribution == 'Red Hat Enterprise Linux'\n")
		playbook.write("  - name: prep\n")
		playbook.write("    command: apt update\n")
		playbook.write("    when: ansible_distribution == 'Debian' or ansible_distribution == 'Ubuntu'\n")
		playbook.write("  - name: upgradable\n")
		playbook.write("    command: yum list updates -q\n")
		playbook.write("    when: ansible_distribution == 'CentOS' or ansible_distribution == 'Red Hat Enterprise Linux'\n")
		playbook.write("  - name: upgradable\n")
		playbook.write("    command: apt list --upgradable\n")
		playbook.write("    when: ansible_distribution == 'Debian' or ansible_distribution == 'Ubuntu'\n")
		playbook.close()

	def generate_playbook_update_client(self, task_id, client, package_list):
		self.playbook = self.playbooks_dir + task_id + '_' + client.ID + '.yml'
		playbook = open(self.playbook, "w")
		playbook.write("---\n")
		playbook.write("- hosts: " + client.IP + "\n")
		playbook.write("  remote_user: yarus\n")
		playbook.write("  gather_facts: no\n")
		playbook.write("  become: true\n")
		playbook.write("  tasks:\n")
		playbook.write("  - name: upgrade\n")
		if client.type == 'YUM':
			playbook.write("    yum:\n")
		elif client.type == 'APT':
			playbook.write("    apt:\n")			
		playbook.write("     name: \"{{ item }}\"\n")
		playbook.write("     state: latest\n")
		playbook.write("    with_items:  \n")
		for package in package_list:
			playbook.write("     - " + package + "  \n")
		playbook.close()
	def generate_playbook_update_group(self, task_id, group, groupeds, package_list):
			self.playbook = self.playbooks_dir + task_id + '_' + group.ID + '.yml'
			playbook = open(self.playbook, "w")
			playbook.write("---\n")
			playbook.write("- hosts:\n")
			for client in groupeds:
				playbook.write("  - " + client['IP'] + "\n")
			playbook.write("  remote_user: yarus\n")
			playbook.write("  gather_facts: true\n")
			playbook.write("  become: true\n")
			playbook.write("  tasks:\n")
			rpm = False
			deb = False
			for package in package_list:
				if package['type'] == 'rpm':
					rpm = True
				elif package['type'] == 'deb':
					deb = True
				if rpm and deb:
					break
			if rpm:
				playbook.write("  - name: upgrade\n")
				playbook.write("    yum:\n")
				playbook.write("     name: \"{{ item }}\"\n")
				playbook.write("     state: latest\n")
				playbook.write("    with_items:  \n")
				for package in package_list:
					if package['type'] == 'rpm':
						playbook.write("     - " + package['name'] + "  \n")
				playbook.write("    when: ansible_distribution == 'CentOS' or ansible_distribution == 'Red Hat Enterprise Linux'\n")				
			if deb:
				playbook.write("  - name: upgrade\n")
				playbook.write("    apt:\n")
				playbook.write("     name: \"{{ item }}\"\n")
				playbook.write("     state: latest\n")
				playbook.write("    with_items:  \n")
				for package in package_list:
					if package['type'] == 'deb':
						playbook.write("     - " + package['name'] + "  \n")
				playbook.write("    when: ansible_distribution == 'Debian' or ansible_distribution == 'Ubuntu'\n")
			playbook.close()

	def generate_playbook_update_all_client(self, task_id, client):
		self.playbook = self.playbooks_dir + task_id + '_' + client.ID + '.yml'
		playbook = open(self.playbook, "w")
		playbook.write("---\n")
		playbook.write("- hosts: " + client.IP + "\n")
		playbook.write("  remote_user: yarus\n")
		playbook.write("  gather_facts: no\n")
		playbook.write("  become: true\n")
		playbook.write("  tasks:\n")
		playbook.write("  - name: upgrade\n")
		if client.type == 'YUM':
			playbook.write("    yum:\n")
		elif client.type == 'APT':
			playbook.write("    apt:\n")
		playbook.write("     name: '*'\n")
		playbook.write("     state: latest\n")
		playbook.close()
	def generate_playbook_update_all_group(self, task_id, group, groupeds):
			self.playbook = self.playbooks_dir + task_id + '_' + group.ID + '.yml'
			playbook = open(self.playbook, "w")
			playbook.write("---\n")
			playbook.write("- hosts:\n")
			for client in groupeds:
				playbook.write("  - " + client['IP'] + "\n")
			playbook.write("  remote_user: yarus\n")
			playbook.write("  gather_facts: true\n")
			playbook.write("  become: true\n")
			playbook.write("  tasks:\n")			
			playbook.write("  - name: upgrade\n")
			playbook.write("    yum:\n")
			playbook.write("     name: '*'\n")
			playbook.write("     state: latest\n")		
			playbook.write("    when: ansible_distribution == 'CentOS' or ansible_distribution == 'Red Hat Enterprise Linux'\n")			
			playbook.write("  - name: upgrade\n")
			playbook.write("    command: apt-get -y upgrade\n")
			playbook.write("    when: ansible_distribution == 'Debian' or ansible_distribution == 'Ubuntu'\n")
			playbook.close()

	def showplaybook(self, app):
		with open(self.playbook) as file:
			for line in file:
				app.log.logtask(line.strip("\n"))
	def executeplaybook(self, app):
		if self.playbook:
			ansible_cmd = "ansible-playbook " + self.playbook + " -i /opt/yarus/scripts/yarus-ansible-inventory.py"
			app.log.logtask(ansible_cmd)
			process = subprocess.Popen(ansible_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			(output, error) = process.communicate()
			result = process.wait()
			response = output.decode('ascii')
			return response
		return False
	def clean(self):
		if os.path.isfile(self.playbook):
			os.remove(self.playbook)

	
