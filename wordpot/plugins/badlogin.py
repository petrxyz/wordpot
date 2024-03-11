from wordpot.plugins_manager import BasePlugin

class Plugin(BasePlugin):
    def run(self):
        # Initialize template vars dict 
        self.outputs['template_vars'] = {} 

        # First check if the file is wp-login.php
        if not (self.inputs['filename'] == 'wp-login' and self.inputs['ext'] == 'php'):
            return 

        # Logic
        origin = self.inputs['request'].remote_addr

        if self.inputs['request'].method == 'POST':
            print("Confirmed that POST = {}".format(self.inputs['request'].method))
            username = self.inputs['request'].form['log']
            password = self.inputs['request'].form['pwd']
            self.outputs['log_json'] = self.to_json_log(username=username, password=password, plugin="badlogin")
            self.outputs['template_vars']['BADLOGIN'] = True
            self.outputs['template'] = 'wp-login.html'
        else:
            self.outputs['log_json'] = self.to_json_log(info="enumeration", plugin="badlogin")
            self.outputs['template_vars']['BADLOGIN'] = False 
            self.outputs['template'] = 'wp-login.html'

        return
