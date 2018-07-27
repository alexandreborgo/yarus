
import subprocess

class Ansible:

	def ping(self, client_ip):
		ansible_cmd = "ansible -i /var/lib/yarus/yarus-ansible-inventory.py " + client_ip + " -m ping"
		result = subprocess.call(ansible_cmd, shell=True)

		if result != 0:
			return False
		else:
			return True

	def executeplaybook(self, playbook):
		ansible_cmd = "ansible-playbook " + playbook + "  -i /var/lib/yarus/yarus-ansible-inventory.py"
		process = subprocess.Popen(ansible_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		(output, error) = process.communicate()
		result = process.wait()
		response = output.decode('ascii')
		if result != 0:
			return False
		else:
			return response

	def generate_playbook_config_yum_client(self, client, file):
		playbook = open('/var/lib/yarus/playbooks/' + client.ID + '.yml', "w")
		playbook.write("---\n")
		playbook.write("- hosts: " + client.IP + "\n")
		playbook.write("  remote_user: root\n")
		playbook.write("  gather_facts: no\n")
		playbook.write("  tasks:\n")
		playbook.write("  - name: Remove all previous configuration\n")
		playbook.write("    file:\n")
		playbook.write("      state: absent\n")
		playbook.write("      path: /etc/yum.repos.d/\n")
		playbook.write("  - name: Create the empty directory yum.repos.d\n")
		playbook.write("    file:\n")
		playbook.write("      state: directory\n")
		playbook.write("      path: /etc/yum.repos.d/\n")
		playbook.write("  - name: Copy reposiroties configuration file to the client\n")
		playbook.write("    copy:\n")
		playbook.write("      src: " + file + "\n")
		playbook.write("      dest: /etc/yum.repos.d/\n")
		playbook.write("      owner: root\n")
		playbook.write("      group: root\n")
		playbook.close()
		return '/var/lib/yarus/playbooks/' + client.ID + '.yml'
	def generate_playbook_config_apt_client(self, client, file):
		playbook = open('/var/lib/yarus/playbooks/' + client.ID + '.yml', "w")
		playbook.write("---\n")
		playbook.write("- hosts: " + client.IP + "\n")
		playbook.write("  remote_user: root\n")
		playbook.write("  gather_facts: no\n")
		playbook.write("  tasks:\n")
		playbook.write("  - name: Remove all previous configuration\n")
		playbook.write("    file:\n")
		playbook.write("      state: absent\n")
		playbook.write("      path: /etc/apt/sources.list\n")
		playbook.write("  - name: Copy reposiroties configuration file to the client\n")
		playbook.write("    copy:\n")
		playbook.write("      src: " + file + "\n")
		playbook.write("      dest: /etc/apt/sources.list\n")
		playbook.write("      owner: root\n")
		playbook.write("      group: root\n")
		playbook.close()
		return '/var/lib/yarus/playbooks/' + client.ID + '.yml'

	def generate_playbook_upgradable_yum_client(self, client):
		playbook = open('/var/lib/yarus/playbooks/' + client.ID + '.yml', "w")
		playbook.write("---\n")
		playbook.write("- hosts: " + client.IP + "\n")
		playbook.write("  remote_user: root\n")
		playbook.write("  gather_facts: no\n")
		playbook.write("  tasks:\n")
		playbook.write("  - name: upgradable\n")
		playbook.write("    command: yum list updates -q\n")
		playbook.close()
		return '/var/lib/yarus/playbooks/' + client.ID + '.yml'
	def generate_playbook_upgradable_apt_client(self, client):
		playbook = open('/var/lib/yarus/playbooks/' + client.ID + '.yml', "w")
		playbook.write("---\n")
		playbook.write("- hosts: " + client.IP + "\n")
		playbook.write("  remote_user: root\n")
		playbook.write("  gather_facts: no\n")
		playbook.write("  tasks:\n")
		playbook.write("  - name: update\n")
		playbook.write("    command: apt-get update\n")
		playbook.write("  - name: upgradable\n")
		playbook.write("    command: apt list  --upgradable\n")
		playbook.close()
		return '/var/lib/yarus/playbooks/' + client.ID + '.yml'

	def generate_playbook_update_client(self, client, package_list):
		playbook = open('/var/lib/yarus/playbooks/' + client.ID + '.yml', "w")
		playbook.write("---\n")
		playbook.write("- hosts: " + client.IP + "\n")
		playbook.write("  remote_user: root\n")
		playbook.write("  gather_facts: no\n")
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
		playbook.write("  - name: upgradable\n")
		if client.type == 'YUM':
			playbook.write("    command: yum list updates -q\n")
		elif client.type == 'APT':
			playbook.write("    command: apt list  --upgradable\n")
		playbook.close()
		return '/var/lib/yarus/playbooks/' + client.ID + '.yml'

	def generate_playbook_check_group(self, group, grouped):
		playbook = open('/var/lib/yarus/playbooks/' + group.ID + '.yml', "w")
		playbook.write("---\n")
		playbook.write("- hosts:\n")
		for client in grouped:
			playbook.write("  - " + client['IP'] + "\n")
		playbook.write("  remote_user: root\n")
		playbook.write("  gather_facts: no\n")
		playbook.write("  tasks:\n")
		playbook.write("  - name: check\n")
		playbook.write("    ping:\n")		
		playbook.close()
		return '/var/lib/yarus/playbooks/' + group.ID + '.yml'
	
