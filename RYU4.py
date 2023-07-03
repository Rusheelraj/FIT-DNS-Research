from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, udp
from ryu.lib.packet.stream_parser import StreamParser
from ryu.lib import hub

from ryu.ofproto import ether
from ryu.lib.packet import in_proto

import threading

class DNSController(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    DNS_PORT = 53
    DNS_QUERY_TYPE = 1  # DNS query type A

    def __init__(self, *args, **kwargs):
        super(DNSController, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        print("Initializing DNSController...")
        self.vm1_ip = '192.168.233.11'  # Replace with the actual IP address of vm1
        self.vm2_ip = '192.168.233.10'  # Replace with the actual IP address of vm2
        self.attack_threshold = 100  # Define the threshold for attack detection
        self.current_target = self.vm1_ip
        self.dns_req_count = 0
        self.lock = threading.Lock()

        # Start a separate thread to periodically check for attacks
        self.monitor_thread = hub.spawn(self._monitor_network)

    def _monitor_network(self):
        while True:
            self.lock.acquire()
            if self.dns_req_count > self.attack_threshold:
                print("Attack detected!")
                self.current_target = self.vm2_ip
            else:
                print("No attack detected.")
                self.current_target = self.vm1_ip
            self.lock.release()

            hub.sleep(5)  # Adjust the interval between monitoring cycles as needed

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        print("Received switch features event...")
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # Install a table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(datapath=datapath, priority=priority, match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        try:
            pkt = packet.Packet(msg.data)
        except StreamParser.TooSmallException:
            return

        eth = pkt.get_protocol(ethernet.ethernet)
        ip_pkt = pkt.get_protocol(ipv4.ipv4)
        udp_pkt = pkt.get_protocol(udp.udp)

        if eth.ethertype == ether.ETH_TYPE_IP and ip_pkt.proto == in_proto.IPPROTO_UDP and udp_pkt.dst_port == self.DNS_PORT:
            self.dns_req_count += 1

            match = parser.OFPMatch(in_port=msg.match['in_port'], eth_type=ether.ETH_TYPE_IP, ip_proto=in_proto.IPPROTO_UDP, udp_dst=self.DNS_PORT)
            actions = [parser.OFPActionSetField(ipv4_dst=self.current_target), parser.OFPActionOutput(ofproto.OFPP_NORMAL)]
            self.add_flow(datapath, 1, match, actions)

        else:
            actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
            out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.match['in_port'], actions=actions)
            datapath.send_msg(out)

