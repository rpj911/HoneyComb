# System Overview
This is a Revolution CT system of GE Healthcare. There are several nodes linked by 1Gbps cable or 10Gbps fibre. You will only run on the host node and if you want to execute commands on other nodes, you can use ssh to login and execute commands remotely.

# System Nodes
The whole CT system is composed with several nodes. This nodes are all running OS of version SLES15. During the installation of the whole CT system, remote nodes are installed via a complicated procedure, including NFS Root Creation, Network Configuration, Virtual Machine Defination and so on.

## Host
This is the operator desktop of the CT system and it monitors all other nodes.

## SDAC/SIG
This is the node of Scan Data Acquisition. SDAC node has high performance network, RAID and multi-cores CPU. It also provides bare metal machine for igc1/2 virtual machine.

## IGC1/2
These nodes is the node of Recon. Except G3 hardware, IGC1/2 are virtaul machine nodes that run on SDAC bare metal.

## XIG1
This node is also a node of Recon while it is a bare metal node like SDAC. Note that XIG1 node only appears in Hyper hardware.

# System Nouns
There are many specific nouns that may occur in user problem description, knowledge, logs and so on. Here are some refrences:
- Obelus: This is a micro-service framework runs on SDAC and IGC nodes. Obelus manages some processes on these nodes. You can use `ssh <node> ps -ef | grep obelus` to check if the obelus processes are running.
- IG: For Image Generation, or Recon(struction). This is the computation node for CT reconstruction. Also, IGC is for IG Computer.
- SDA: For Scan Data Acquisition. SDAC, aka SDA Computer, is the data collection node. 
- Syscab: For short form of Syetem Cabinet, which includes IGCs, SDAC and XIG1(if any). In general, this noun refers to the hardware combination. While the lower case "syscab" is a tool set that runs on Host to install/diagnostic/query of the System Cabinet hardware. 