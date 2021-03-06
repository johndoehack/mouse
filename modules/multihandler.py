import os
from modules import helper as h
import threading, socket, time, sys

DOJ='\033[1;34m[*]\033[0;97m'

class MultiHandler:
	def __init__(self,server):
		self.server = server
		self.thread = None
		self.sessions_id = dict()
		self.sessions_uid = dict()
		self.handle = h.WHITE+"("+h.GREEN + "MultiHandler" + h.WHITE +")> "
		self.is_running = False


	def update_session(self,current_session,new_session):
		current_session.conn = new_session.conn
		current_session.username = new_session.username
		current_session.hostname = new_session.hostname
		current_session.type = new_session.type
		current_session.needs_refresh = False
		sys.stdout.write("\n"+current_session.get_handle())
		sys.stdout.flush()


	def background_listener(self):
		self.server.is_multi = True
		self.is_running = True
		id_number = 1
		while 1:
			if self.is_running:
				session = self.server.listen_for_stager()
				if session:
					if session.uid in self.sessions_uid.keys():
						if self.sessions_uid[session.uid].needs_refresh:
							self.update_session(self.sessions_uid[session.uid],session)
						continue
					else:
						self.sessions_uid[session.uid] = session
						self.sessions_id[id_number] = session
						session.id = id_number
						id_number += 1
						sys.stdout.write("\n{0} Session {1} opened.{2}\n{3}".format(DOJ,str(session.id),h.WHITE,self.handle))
						sys.stdout.flush()
			else:
				return


	def start_background_server(self):
		self.thread = threading.Thread(target=self.background_listener)
		self.thread.setDaemon(False)
		self.thread.start()


	def close_all_sessions(self):
		h.info_general("Cleaning up...")
		for key in self.sessions_id.keys():
			session = self.sessions_id[key]
			session.disconnect(False)


	def show_session(self,session):
		try:
			print str(session.id) + " | " +\
			session.hostname + "@" + session.username + " | " + \
			str(session.conn.getpeername()[0]) 
		except Exception as e:
			h.info_error(str(e))


	def list_sessions(self):
		if not self.sessions_id:
			h.info_general("No active sessions.")
		else:
			for key in self.sessions_id:
				self.show_session(self.sessions_id[key])


	def interact_with_session(self,session_number):
		if not session_number:
			print "Usage: interact <session>"
			return
		try:
			self.sessions_id[int(session_number)].interact()
		except:
			h.info_error("Invalid session number!")


	def close_session(self,session_number):
		if not session_number:
			print "Usage: close <session_number>"
			return
		try:
			session = self.sessions_id[int(session_number)]
			session.disconnect(False)
			h.info_general('Closing session ' + session_number + '...')
		except Exception as e:
			print e
			h.info_error("Invalid session number!")


	def stop_server(self):
		self.close_all_sessions()
		self.is_running = False
		if self.thread:
			socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self.server.host,self.server.port))
			self.thread.join()
		time.sleep(0.5)


	def show_command(self,name,description):
                print("\n\033[0mMultiHandler Commands")
                print("=====================")
		os.system("cat resources/multihandler_cmds.txt")
		print("")

	def show_commands(self):
		print("\n\033[0mMultiHandler Commands")
                print("=====================")
		os.system("cat resources/multihandler_cmds.txt")
		print("")


	def interact(self):
		h.info_general("Listening on port {0}...".format(self.server.port))
		h.info_general("Type \"help\" for commands.")
		while 1:
			try:
				input_data = raw_input(self.handle)
				if not input_data:
					continue
				cmd = input_data.split()[0]
				args = input_data[len(cmd):].strip()
				if cmd == "interact":
					self.interact_with_session(args)
				elif cmd == "close":
					self.close_session(args)
				elif cmd == "sessions":
					self.list_sessions()
				elif cmd == "help":
					self.show_commands()
				elif cmd == "exit":
					self.stop_server()
					return
				else:
					h.info_error("Unrecognized command!")

			except KeyboardInterrupt:
				sys.stdout.write("\n")
				self.stop_server()
				return

