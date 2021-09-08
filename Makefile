
include Makefile.frag

SHELL := /bin/bash

SERVER_MNT   = /home/farzam/mnt/nfs
BOARD_MNT    = /home/xilinx/mnt/nfs_client
IP_GROUP     = 192.168.2.
SERVER_IP    = $(IP_GROUP)1
SERVER_UNAME = farzam
CLIENT_UNAME = xilinx
CLIENT_PASS  = xilinx
MY_IP        = $(shell ifconfig | awk '/$(IP_GROUP)/ {print $$2}')
#BOARDS       = $(filter-out $(SERVER_IP),$(shell nmap -sn -oG - $(IP_GROUP)90-99 | awk '/Host:/ {print $$2}'))
BOARDS       = 192.168.2.95 192.168.2.96 192.168.2.97 192.168.2.98 192.168.2.99
SSH_SESSIONS = $(subst :ssh,,$(shell ss | grep -i ':ssh' | awk '/:ssh/ {print $$6}'))

define ssh2board
	ssh $(CLIENT_UNAME)@$1 $2 "echo $(CLIENT_PASS) | sudo -S $3"
endef

ifeq ($(SERVER_IP),$(MY_IP))

query_boards:
	@echo $(BOARDS)

query_ssh:
	@echo $(SSH_SESSIONS)

query_mem:
	for ip in $(BOARDS); do \
		$(call ssh2board,$$ip,,cat /proc/meminfo); \
	done

$(SERVER_MNT)/%/zynq-parrot:
	git clone git@github.com:black-parrot-hdk/zynq-parrot.git $@ --branch spectests

gen_dirs:
	git clone git@github.com:black-parrot-hdk/zynq-parrot.git $(SERVER_MNT)/zynq-parrot --branch spectests
	for ip in $(BOARDS); do \
		mkdir -p $(SERVER_MNT)/$$ip; \
		cp -r $(SERVER_MNT)/zynq-parrot $(SERVER_MNT)/$$ip/zynq-parrot; \
	done
	rm -rf $(SERVER_MNT)/zynq-parrot

clean_dirs:
	rm -rf $(SERVER_MNT)/$(IP_GROUP)*

mount_boards:
	for ip in $(BOARDS); do \
		$(call ssh2board,$$ip,,mkdir -p $(BOARD_MNT)); \
		$(call ssh2board,$$ip,,mount $(SERVER_IP):$(SERVER_MNT) $(BOARD_MNT)); \
	done

unmount_boards:
	for ip in $(BOARDS); do \
		$(call ssh2board,$$ip,,umount $(BOARD_MNT)); \
	done

load_bitstreams:
	for ip in $(BOARDS); do \
		$(call ssh2board,$$ip,-f,$(MAKE) -C $(BOARD_MNT) load_bitstream > /dev/null 2>&1); \
	done

%.run:
	@echo Running $($*_benchs) on $@
	$(call ssh2board,$*,-f,$(MAKE) -C $(BOARD_MNT) run_nbfs NBF_FILES=\"$(addsuffix .nbf,$(addprefix $(BOARD_MNT)/bench/,$($*_benchs)))\" > /dev/null 2>&1)

run_benchs: $(foreach ip,$(BOARDS),$(ip).run)

else

ZPARROT_DIR = $(BOARD_MNT)/$(MY_IP)/zynq-parrot
FPGA_DIR    = $(ZPARROT_DIR)/cosim/black-parrot-example/fpga
BITSTREAM   = $(FPGA_DIR)/blackparrot_bd_1.tar.xz.b64

$(BITSTREAM): | $(ZPARROT_DIR)
	cp $(BOARD_MNT)/$(notdir $(BITSTREAM)) $(BITSTREAM)

load_bitstream: $(BITSTREAM) | $(ZPARROT_DIR)
	cat /proc/meminfo > $(BOARD_MNT)/$(MY_IP)/load.log 2>&1
	$(MAKE) -C $(FPGA_DIR) unpack_bitstream >> $(BOARD_MNT)/$(MY_IP)/load.log 2>&1
	$(MAKE) -C $(FPGA_DIR) load_bitstream >> $(BOARD_MNT)/$(MY_IP)/load.log 2>&1

run: $(NBF_FILE) | $(ZPARROT_DIR)
	$(MAKE) -C $(FPGA_DIR) run NBF_FILE=$< > $(BOARD_MNT)/$(MY_IP)/$(notdir $<).run.log 2>&1

run_nbfs: $(NBF_FILES)
	for nbf in $(NBF_FILES); do \
		$(MAKE) run NBF_FILE=$$nbf; \
	done

endif
