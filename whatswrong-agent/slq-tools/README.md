# slq-tools



## Catagories

### For General Use
Some useful tiny tools that can be used in daily trouble shooting and development.
| Tool | Description |
|:--------------|:-------------|
|**`dumptimers`**|Used to dump timers.log of cup process|

### For New Scan DB Integration On Revo
Some useful tiny tool that can be used in the integration test of New Scan DB. There are some scenario like: 
- The performance of New Scan DB need to be tested in full scan (300 exams or 1500 scans)case. We need to fulfill the db before testing, and remove these scans after testing.

| Tool | Description |
|:--------------|:-------------|
|**`remove_scans`**|For New Scan DB integration on Revo test. Remove all installed scans after full scan db stress test. Also, a scankey pattern can be specified to restrict the removement.|
|**`mock_ffp`**|For New Scan DB integration on Revo test. Generate mocked FFP with all the same content but different exam_number. Need to be used along with AcqHeaderDefination/ and inspect_ffp_file/

### For HUE Service Integration on CT System
| Tool | Description |
|:--------------|:-------------|
|**`huetool`**|Provide a command line method to interact with HUE Service, for debug purpose mainly.|

### For Both HUE Service and New Scan DB Integration
| Tool | Description |
|:--------------|:-------------|
|**`extractHDF5`**|A tool used to extract specified node from saved HDF5 archive file from New Scan DB and HUE|

### For Hyper
| Tool | Description |
|:--------------|:-------------|
|**`cat_runner`**|A tool used to run catfiles and extract recon_timings log (use drive). For performance test, run a catfile for 3 times (by default, use --times to specify) and compute average TTFI/FPS/TTLI. Also, if need to filter-out some protocol, use --protocol-filter.|

### Agent Tools
AI Agents that can be used to diagnostic/trouble-shooting in CT system.
| Tool | Description |
|:--------------|:-------------|
|**`whatswrong-agent`**|A agent that can be used to diagnostic problems on console/simulator/Bay. The only required input is the problem description in natural language. For more detail, see README under whatswrong-agent/ |