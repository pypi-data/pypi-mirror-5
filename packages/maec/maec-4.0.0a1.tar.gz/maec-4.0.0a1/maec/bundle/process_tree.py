#MAEC Bundle Class

#Copyright (c) 2013, The MITRE Corporation
#All rights reserved.

#Compatible with MAEC v4.0
#Last updated 5/13/2013

import maec
import maec.bindings.maec_bundle as bundle_binding
from cybox.objects.process_object import Process
from maec.bundle.action_reference_list import ActionReferenceList
       
class ProcessTree(maec.Entity):
    def init(self, root_process = None):
        super(ProcessTree, self).__init__()
        self.processtree.set_Root_Process(root_process)
        self.root_process = root_process
        
    def set_root_process(self, root_process):
        self.root_process = root_process
        
    def to_obj(self):
        process_tree_obj = bundle_binding.ProcessTreeType()
        if self.root_process is not None:
            processtree.set_Root_Process(self.root_process.to_obj())
        return process_tree_obj

    def to_dict(self):
        process_tree_dict = {}
        if self.root_process is not None:
            process_tree_dict['root_process'] = self.root_process.to_dict()
        return process_tree_dict

    @staticmethod
    def from_dict(process_tree_dict):
        if not process_tree_dict:
            return None
        process_tree_ = ProcessTree()
        process_tree_.root_process = ProcessTreeNode.from_dict(process_tree_dict.get('process_tree'))
        return process_tree_

    @staticmethod
    def from_obj(process_tree_obj):
        if not process_tree_obj:
            return None
        process_tree_ = ProcessTree()
        process_tree_.root_process = ProcessTreeNode.from_obj(process_tree_obj.get_Root_Process())
        return process_tree_
    
    
class ProcessTreeNode(Process):
    superclass = Process

    def init(self, id = None, parent_action_idref = None):
        super(ProcessTreeNode, self).__init__()
        self.id = id
        self.parent_action_idref = parent_action_idref
        self.initiated_actions = None
        self.spawned_processes = []
        self.injected_processes = []      

    def add_spawned_process(self, process_node):
        self.spawned_processes.append(process_node)
        
    def add_injected_process(self, process_node):
        self.injected_processes.append(process_node)
        
    def add_initiated_action(self, action_id):
        self.initiated_actions.append(action_id)
        
    def set_id(self, id):
        self.id = id
        
    def set_parent_action(self, parent_action_id):
        self.parent_action_idref = parent_action_id
        
    def to_obj(self):
        process_tree_node_obj = super(ProcessTreeNode, self).to_obj(bundle_binding.ProcessTreeNodeType())
        if self.id is not None : process_tree_node_obj.set_id(self.id)
        if self.parent_action_idref is not None : process_tree_node_obj.set_parent_action_idref(self.parent_action_idref)
        if len(self.initiated_actions) > 0: process_tree_node_obj.set_Initiated_Actions(self.initiated_actions.to_obj())
        if len(self.spawned_processes) > 0: 
            for spawned_process in self.spawned_processes:
                process_tree_node_obj.add_Spawned_Process(spawned_process.to_obj())
        if len(self.injected_processes) > 0: 
            for injected_process in self.injected_processes:
                process_tree_node_obj.add_Injected_Process(injected_process.to_obj())
        return process_tree_node_obj

    def to_dict(self):
        process_tree_node_dict = super(ProcessTreeNode, self).to_dict()
        if self.id is not None : process_tree_node_dict['id'] = self.id
        if self.parent_action_idref is not None : process_tree_node_dict['parent_action_idref'] = self.parent_action_idref
        if len(self.initiated_actions) > 0: process_tree_node_dict['initiated_actions'] = self.initiated_actions.to_list()
        if len(self.spawned_processes) > 0:
            spawned_process_list = []
            for spawned_process in self.spawned_processes:
                spawned_process_list.append(spawned_process.to_dict())
            process_tree_node_dict['spawned_processes'] = spawned_process_list
        if len(self.injected_processes) > 0: 
            injected_process_list = []
            for injected_process in self.injected_processes:
                injected_process_list.append(injected_process.to_dict())
            process_tree_node_dict['injected_processes'] = injected_process_list
        return process_tree_node_dict

    @staticmethod
    def from_dict(process_tree_node_dict):
        if not process_tree_node_dict:
            return None
        process_tree_node_ = Process.from_dict(process_tree_node_dict, ProcessTreeNode())
        process_tree_node_.id = process_tree_node_dict.get('id')
        process_tree_node_.parent_action_idref = process_tree_node_dict.get('parent_action_idref')
        process_tree_node_.initiated_actions = ActionReferenceList.from_list(process_tree_node_dict.get('initiated_actions'))
        process_tree_node_.spawned_processes = [ProcessTreeNode.from_dict(x) for x in process_tree_node_dict.get('spawned_processes')]
        process_tree_node_.injected_processes = [ProcessTreeNode.from_dict(x) for x in process_tree_node_dict.get('injected_processes')]
        return process_tree_node_

    @staticmethod
    def from_obj(process_tree_node_obj):
        if not process_tree_node_obj:
            return None
        process_tree_node_ = Process.from_obj(process_tree_node_obj, ProcessTreeNode())
        process_tree_node_.id = process_tree_node_obj.get_id()
        process_tree_node_.parent_action_idref = process_tree_node_obj.get_parent_action_idref()
        process_tree_node_.initiated_actions = ActionReferenceList.from_obj(process_tree_node_obj.get_Initiated_Actions())
        process_tree_node_.spawned_processes = [ProcessTreeNode.from_obj(x) for x in process_tree_node_obj.get_Spawned_Process()]
        process_tree_node_.injected_processes = [ProcessTreeNode.from_obj(x) for x in process_tree_node_obj.get_Injected_Process()]
        return process_tree_node_
