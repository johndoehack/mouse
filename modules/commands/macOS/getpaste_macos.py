class command:
    def __init__(self):
        self.name = "getpaste"
        self.description = "Get pasteboard contents."
        self.type = "native"

    def run(self,session,cmd_data):
        print("===================")
        print session.send_command(cmd_data)
        print("===================")
