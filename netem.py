import subprocess
import json

class Netem(object):

   def __init__(self):
      conf = json.load(open('ifaces.conf.json'))
      self.ifaces = conf['ifaces']
      print self.ifaces


   def list_ifaces(self):
      args = ['ls', '/sys/class/net']
      p = subprocess.Popen(args, stdout=subprocess.PIPE)
      output = p.communicate()[0].split()
      output = filter(self.is_allowed_iface, output)
      return output


   def is_allowed_iface(self, dev):
      if dev.encode('utf-8') in self.ifaces:
         return True
      return False


   def add_netem(self, dev):
      assert dev
      args = ['tc', 'qdisc', 'add', 'dev', dev, 'root', 'netem', 'delay', '1ms', '0.1ms', 'loss', '0.01%']
      print args
      p = subprocess.Popen(args, stdout=subprocess.PIPE)
      output = p.communicate()[0]


   def get_netem(self, dev):
      assert dev
      print dev
      args = ['tc', 'qdisc', 'show', 'dev', dev]
      print args
      p = subprocess.Popen(args, stdout=subprocess.PIPE)
      output = p.communicate()[0]
            
      return self.parse_tc(output)


   def parse_tc(self, tc_string):
      val = {'conf': tc_string, 'delay':'none', 'd_var':'none', 'loss':'none'};

      parts = tc_string.split()
      print(parts)

      if len(parts) > 11:
        val['delay'] = parts[9]
        val['d_var'] = parts[10]
        val['loss']  = parts[12]
      print(val)
      return val;


   def set_delay(self, dev, d_size, d_variation='0.01ms', loss='0.001%' ):
      assert dev
      curconf = self.get_netem(dev)
      if not curconf['conf']:
         print "no netem on dev: [%s]. Adding it..." % dev
         self.add_netem(dev)
      print ("dev: [%s] delay: [%s] d_variation: [%s]" \
             % (dev, d_size, d_variation))
      args = ['tc', 'qdisc', 'change', 'dev', dev, 'root', 'netem', 'delay',
              d_size, d_variation, 'loss', loss]
      print args
      p = subprocess.Popen(args, stdout=subprocess.PIPE)
      return self.get_netem(dev)
      

