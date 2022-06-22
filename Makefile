
BP_DIR ?= logs/events/bp-new/
AR_DIR ?= logs/events/cva6-new/

TESTS = 164.gzip 171.swim 172.mgrid 173.applu 177.mesa 181.mcf 183.equake 186.crafty 188.ammp 197.parser 256.bzip2 300.twolf 401.bzip2 410.bwaves 433.milc 437.leslie3d 444.namd 445.gobmk 447.dealII 450.soplex 454.calculix 456.hmmer 458.sjeng 462.libquantum 464.h264ref 471.omnetpp 473.astar 507.cactuBSSN_r 508.namd_r 510.parest_r 531.deepsjeng_r 541.leela_r 544.nab_r 548.exchange2_r 549.fotonik3d_r 557.xz_r 

REPS = $(addsuffix .rep,$(TESTS))
BP_REPS = $(addprefix $(BP_DIR),$(REPS))
AR_REPS = $(addprefix $(AR_DIR),$(REPS))

events:
	python events.py --ar_path $(AR_DIR) --bp_path $(BP_DIR) $(REPS)

groups:
	python groups.py --ar_path $(AR_DIR) --bp_path $(BP_DIR) $(REPS)

bp_stalls:
	python bp_stalls.py $(BP_REPS)

ar_stalls:
	python ar_stalls.py $(AR_REPS)
