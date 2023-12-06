# FloWide Workbench
### version 1.0 released as technical release

FloWide Workbench is an evironment that allows editing and running python based web applications targeting location data processing.

Workbench consists of several different open soruce components, running as separate docker containers.

### [KeyCloak](https://www.keycloak.org/)
Handles authentication and provides OAuth2 login.

### [GitLab](https://about.gitlab.com/)
All application repositories are manged with gitlab and accessible through is API.

### [OpenResty](https://openresty.org/) 
Works as HTTP proxy and servers the [Workbench User interface]( https://github.com/FloWide/workbench-ui )

### [ScriptHandler](https://github.com/FloWide/scripthandler) 
Is responsible for running applications and managing the releases.

Also workbench comes with two other binary only containers to handle data communications and position calculation with FloWide RTLS hardware.

### [BDCL](https://github.com/FloWide/bdcl1) 
Buffering Data Communications Layer (BDCL) is neccesarry to convert the sensor and timing data coming from FloWide RTLS hardware. Container opens 1194 port for static OpenVPN connections to connect it to a router of a FloWide RTLS deployment.

### [SCL](https://github.com/FloWide/scl1)
SCL calulcates the position of trackers that have timing coming from UWB communication layer. In order for positioning to work, service has to be configured. After restart SCL container calls a pre-defined API call and waits for configuration API commands.

## Installation
1.) Check out the repository: git clone https://github.com/FloWide/workbench1
2.) Copy directory to /root/docker-deployment
3.) Set the values in .env file based on the template
4.) Run instal.sh that installs the flowide command line interface
5.) start system with flowide docker up

System will be accessible under the domain configured in the .env file.

Other command can be checked with flowide docker --help





