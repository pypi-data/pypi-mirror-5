#!/usr/bin/python

import os
import sys
import string
import optparse
import jenkins
import urllib
import time
import subprocess
import yaml

import rospkg
import rospkg.distro

BOOTSTRAP_SCRIPT = """
cat &gt; $WORKSPACE/script.sh &lt;&lt;DELIM
#!/usr/bin/env bash
set -o errexit
echo "_________________________________BEGIN SCRIPT______________________________________"
sudo apt-get install --yes ros-ROSDISTRO-ros ros-ROSDISTRO-rospack ros-ROSDISTRO-rosmake ros-ROSDISTRO-rosbuild ros-ROSDISTRO-roslib lsb-release pkg-config ros-ROSDISTRO-rosunit
source /opt/ros/ROSDISTRO/setup.sh

export INSTALL_DIR=/tmp/install_dir
export WORKSPACE=/tmp/ros
export ROS_TEST_RESULTS_DIR=/tmp/ros/test_results
export JOB_NAME=$JOB_NAME
export BUILD_NUMBER=$BUILD_NUMBER
export HUDSON_URL=$HUDSON_URL
export ROS_PACKAGE_PATH=\$INSTALL_DIR/ros_release:\$ROS_PACKAGE_PATH

mkdir -p \$INSTALL_DIR
cd \$INSTALL_DIR

wget  --no-check-certificate https://raw.github.com/ros-infrastructure/dry_prerelease_job_generator/groovy_new/job_generation/hudson_helper
chmod +x  hudson_helper
sudo easy_install -U ros-job_generation
"""

SHUTDOWN_SCRIPT = """
echo "_________________________________END SCRIPT_______________________________________"
DELIM

set -o errexit

rm -rf $WORKSPACE/test_results
rm -rf $WORKSPACE/test_output

wget  --no-check-certificate https://raw.github.com/ros-infrastructure/dry_prerelease_job_generator/master/hudson/scripts/run_chroot.py -O $WORKSPACE/run_chroot.py
chmod +x $WORKSPACE/run_chroot.py
cd $WORKSPACE &amp;&amp; $WORKSPACE/run_chroot.py --distro=UBUNTUDISTRO --arch=ARCH  --ramdisk --hdd-scratch=/home/rosbuild/install_dir --script=$WORKSPACE/script.sh --ssh-key-file=/home/rosbuild/rosbuild-ssh.tar
"""

BOOTSTRAP_SCRIPT_OSX = """
echo "_________________________________BEGIN SCRIPT______________________________________"
source /Users/rosbuild/ros_bootstrap/setup.bash
export ROS_PACKAGE_PATH=$WORKSPACE/ros_release:$ROS_PACKAGE_PATH

wget  --no-check-certificate http://code.ros.org/svn/ros/installers/trunk/hudson/hudson_helper -O $WORKSPACE/hudson_helper
chmod +x  $WORKSPACE/hudson_helper
svn co https://code.ros.org/svn/ros/stacks/ros_release/trunk $WORKSPACE/ros_release
"""

SHUTDOWN_SCRIPT_OSX = """
echo "_________________________________END SCRIPT_______________________________________"
"""


# the supported Ubuntu distro's for each ros distro
ARCHES = ['amd64']

# ubuntu distro mapping to ros distro
UBUNTU_DISTRO_MAP = os_test_platform = {
    'groovy': ['precise']
}

# Path to hudson server
SERVER = 'http://jenkins.ros.org'

# config path
CONFIG_PATH = '/var/www/prerelease_website/jenkins.conf'


EMAIL_TRIGGER="""
        <hudson.plugins.emailext.plugins.trigger.WHENTrigger>
          <email>
            <recipientList></recipientList>
            <subject>$PROJECT_DEFAULT_SUBJECT</subject>
            <body>$PROJECT_DEFAULT_CONTENT</body>
            <sendToDevelopers>SEND_DEVEL</sendToDevelopers>
            <sendToRecipientList>true</sendToRecipientList>
            <contentTypeHTML>false</contentTypeHTML>
            <script>true</script>
          </email>
        </hudson.plugins.emailext.plugins.trigger.WHENTrigger>
"""


hudson_scm_managers = {'svn':"""
  <scm class="hudson.scm.SubversionSCM">
    <locations>
      <hudson.scm.SubversionSCM_-ModuleLocation>
        <remote>STACKURI</remote>
        <local>STACKNAME</local>
      </hudson.scm.SubversionSCM_-ModuleLocation>
    </locations>
    <useUpdate>false</useUpdate>
    <doRevert>false</doRevert>
    <excludedRegions></excludedRegions>
    <includedRegions></includedRegions>
    <excludedUsers></excludedUsers>
    <excludedRevprop></excludedRevprop>
    <excludedCommitMessages></excludedCommitMessages>
  </scm>
""",
                       'hg':"""
  <scm class="hudson.plugins.mercurial.MercurialSCM">
    <source>STACKURI</source>
    <modules></modules>
    <subdir>STACKNAME</subdir>
    <clean>false</clean>
    <forest>false</forest>
    <branch>STACKBRANCH</branch>
  </scm>
""",
                       'bzr':"""
  <scm class="hudson.plugins.bazaar.BazaarSCM">
    <source>STACKURI STACKNAME</source>
    <clean>false</clean>
  </scm>
""",
                       'git':"""

  <scm class="hudson.plugins.git.GitSCM">
    <configVersion>1</configVersion>
    <remoteRepositories>
      <org.spearce.jgit.transport.RemoteConfig>
        <string>origin</string>
        <int>5</int>

        <string>fetch</string>
        <string>+refs/heads/*:refs/remotes/origin/*</string>
        <string>receivepack</string>
        <string>git-upload-pack</string>
        <string>uploadpack</string>
        <string>git-upload-pack</string>

        <string>url</string>
        <string>STACKURI</string>
        <string>tagopt</string>
        <string></string>
      </org.spearce.jgit.transport.RemoteConfig>
    </remoteRepositories>
    <branches>

      <hudson.plugins.git.BranchSpec>
        <name>STACKBRANCH</name>
      </hudson.plugins.git.BranchSpec>
    </branches>
    <localBranch></localBranch>
    <mergeOptions/>
    <recursiveSubmodules>false</recursiveSubmodules>
    <doGenerateSubmoduleConfigurations>false</doGenerateSubmoduleConfigurations>

    <authorOrCommitter>Hudson</authorOrCommitter>
    <clean>false</clean>
    <wipeOutWorkspace>false</wipeOutWorkspace>
    <buildChooser class="hudson.plugins.git.util.DefaultBuildChooser"/>
    <gitTool>Default</gitTool>
    <submoduleCfg class="list"/>
    <relativeTargetDir>STACKNAME</relativeTargetDir>

    <excludedRegions></excludedRegions>
    <excludedUsers></excludedUsers>
  </scm>
"""
}

def stack_to_deb(stack_name, distro_name):
    return '-'.join(['ros', distro_name, stack_name.replace('_','-')])

def stacks_to_debs(stack_list, distro_name):
    if not stack_list or len(stack_list) == 0:
        return ''
    return ' '.join([stack_to_deb(s, distro_name) for s in stack_list])

def stacks_to_rosinstall(stack_list, stack_map, branch):
    res = []
    for s in stack_list:
        if s in stack_map:
            res.extend(stack_map[s].vcs_config.to_rosinstall(s, branch, anonymous=True))
        else:
            print 'Stack "%s" is not in stack list. Not adding this stack to rosinstall file'%s
    return yaml.dump(res)

def get_depends_one(stack):
    name = '%s-%s'%(stack.name, stack.version)
    url = urllib.urlopen('http://ros-dry-releases.googlecode.com/svn/download/stacks/%s/%s/%s.yaml'%(stack.name, name, name))
    conf = url.read()
    if '404 Not Found' in conf:
        print 'Could not get dependencies of stack %s with version %s'%(stack.name, stack.version)
        return []
    depends = yaml.load(conf)['depends']
    if depends:
        return depends
    else:
        print 'Stack %s with version %s does not have any dependencies'%(stack.name, stack.version)
        return []

def get_depends_all(distro_obj, stack_name, depends_all):
    start_depth = len(depends_all)
    print start_depth, " depends all ", stack_name
    if not stack_name in depends_all:
        depends_all.append(stack_name)
        try:
            if stack_name in distro_obj.stacks:
                for d in get_depends_one(distro_obj.stacks[stack_name]):
                    get_depends_all(distro_obj, d, depends_all)
            else:
                print >> sys.stderr, "WARNING: [%s] not in rosdistro file, assuming catkin-ized"%(stack_name)
        except KeyError as ex:
            print "Exception when processing %s.  Key %s is not in distro_obj.stacks: %s"%(stack_name, ex, ", ".join([s for s in distro_obj.stacks]))
            print "depends_all is %s"%(', '.join(depends_all))
            raise ex
    print start_depth, " DEPENDS_ALL ", stack_name, " end depth ", len(depends_all)

def get_environment():
    my_env = os.environ
    my_env['WORKSPACE'] = os.getenv('WORKSPACE', '')
    my_env['INSTALL_DIR'] = os.getenv('INSTALL_DIR', '')
    #my_env['HOME'] = os.getenv('HOME', '')
    my_env['HOME'] = os.path.expanduser('~')
    my_env['JOB_NAME'] = os.getenv('JOB_NAME', '')
    my_env['BUILD_NUMBER'] = os.getenv('BUILD_NUMBER', '')
    my_env['ROS_TEST_RESULTS_DIR'] = os.getenv('ROS_TEST_RESULTS_DIR', my_env['WORKSPACE']+'/test_results')
    my_env['PWD'] = os.getenv('WORKSPACE', '')
    return my_env


def get_options(required, optional):
    parser = optparse.OptionParser()
    ops = required + optional
    if 'os' in ops:
        parser.add_option('--os', dest = 'os', default='ubuntu', action='store',
                          help='OS name')
    if 'rosdistro' in ops:
        parser.add_option('--rosdistro', dest = 'rosdistro', default=None, action='store',
                          help='Ros distro name')
    if 'stack' in ops:
        parser.add_option('--stack', dest = 'stack', default=None, action='append',
                          help='Stack name')
    if 'email' in ops:
        parser.add_option('--email', dest = 'email', default=None, action='store',
                          help='Email address to send results to')
    if 'arch' in ops:
        parser.add_option('--arch', dest = 'arch', default=None, action='append',
                          help='Architecture to test')
    if 'ubuntu' in ops:
        parser.add_option('--ubuntu', dest = 'ubuntu', default=None, action='append',
                          help='Ubuntu distribution to test')
    if 'repeat' in ops:
        parser.add_option('--repeat', dest = 'repeat', default=0, action='store',
                          help='How many times to repeat the test')
    if 'source-only' in ops:
        parser.add_option('--source-only', dest = 'source_only', default=False, action='store_true',
                          help="Build everything from source, don't use Debian packages")
    if 'delete' in ops:
        parser.add_option('--delete', dest = 'delete', default=False, action='store_true',
                          help='Delete jobs from Hudson')
    if 'wait' in ops:
        parser.add_option('--wait', dest = 'wait', default=False, action='store_true',
                          help='Wait for running jobs to finish to reconfigure them')
    if 'rosinstall' in ops:
        parser.add_option('--rosinstall', dest = 'rosinstall', default=None, action='store',
                          help="Specify the rosinstall file that refers to unreleased code.")
    if 'overlay' in ops:
        parser.add_option('--overlay', dest = 'overlay', default=None, action='store',
                          help='Create overlay file')
    if 'variant' in ops:
        parser.add_option('--variant', dest = 'variant', default=None, action='store',
                          help="Specify the variant to create a rosinstall for")
    if 'database' in ops:
        parser.add_option('--database', dest = 'database', default=None, action='store',
                          help="Specify database file")

    (options, args) = parser.parse_args()


    # make repeat an int
    if 'repeat' in ops:
        options.repeat = int(options.repeat)

    # check if required arguments are there
    for r in required:
        if not eval('options.%s'%r):
            print 'You need to specify "--%s"'%r
            return (None, args)

    # postprocessing
    if 'email' in ops and options.email and not '@' in options.email:
        options.email = options.email + '@willowgarage.com'


    # check if rosdistro exists
    if 'rosdistro' in ops and (not options.rosdistro or not options.rosdistro in UBUNTU_DISTRO_MAP.keys()):
        print 'You provided an invalid "--rosdistro %s" argument. Options are %s'%(options.rosdistro, UBUNTU_DISTRO_MAP.keys())
        return (None, args)

    # check if stacks exist

    if 'stack' in ops and options.stack:
        distro_name = options.rosdistro
        distro_obj = rospkg.distro.load_distro(rospkg.distro.distro_uri(distro_name))
        for s in options.stack:
            if not s in distro_obj.stacks:
                print 'Stack "%s" does not exist in the %s disro file.'%(s, options.rosdistro)
                print 'You need to add this stack to the rosdistro file'
                return (None, args)

    # check if variant exists
    if 'variant' in ops and options.variant:
        distro_name = options.rosdistro
        distro_obj = rospkg.distro.load_distro(rospkg.distro.distro_uri(distro_name))
        if not options.variant in distro_obj.variants:
                print 'Variant "%s" does not exist in the %s disro file.'%(options.variant, options.rosdistro)
                return (None, args)

    return (options, args)

def job_is_running(jenkins_obj, name):
    """
    Test if a job is running
    @param name The job name
    """
    info = jenkins_obj.get_job_info(name)
    if 'color' in info:
        if string.find(info['color'], "_anime") > 0:
            return True
    return False

def schedule_jobs(jobs, wait=False, delete=False, start=False, hudson_obj=None):
    # create hudson instance
    if not hudson_obj:
        info = urllib.urlopen(CONFIG_PATH).read().split(',')
        hudson_obj = jenkins.Jenkins(SERVER, info[0], info[1])

    def build_job(jenkins_obj, job_name):
        #return jenkins_obj.build_job(job_name)
        # replicate internal implementation of Jenkins.build_job()
        import urllib2
        if not jenkins_obj.job_exists(job_name):
            raise jenkins.JenkinsException('no such job[%s]' % (job_name))
        # pass parameters to create a POST request instead of GET
        return jenkins_obj.jenkins_open(urllib2.Request(jenkins_obj.build_job_url(job_name), 'foo=bar'))

    finished = False
    while not finished:
        jobs_todo = {}
        for job_name in jobs:
            exists = hudson_obj.job_exists(job_name)

            # job is already running
            if exists and job_is_running(hudson_obj, job_name):
                jobs_todo[job_name] = jobs[job_name]
                print "Not changing job %s because it is still running"%job_name

            # reconfigure job
            elif exists and not delete:
                hudson_obj.reconfig_job(job_name, jobs[job_name])
                if start:
                    build_job(hudson_obj, job_name)
                print " - %s"%job_name

            # delete job
            elif exists and delete:
                hudson_obj.delete_job(job_name)
                print " - deleted job %s"%job_name

            # create job
            elif not exists and not delete:
                hudson_obj.create_job(job_name, jobs[job_name])
                if start:
                    build_job(hudson_obj, job_name)
                print " - %s"%job_name

        if wait and len(jobs_todo) > 0:
            jobs = jobs_todo
            jobs_todo = {}
            time.sleep(10.0)
        else:
            finished = True


def get_rosdistro_file(distro_name):
    return 'http://ros-dry-releases.googlecode.com/svn/trunk/distros/%s.rosdistro'%distro_name


def get_email_triggers(when, send_devel=True):
    triggers = ''
    for w in when:
        trigger = EMAIL_TRIGGER
        trigger = trigger.replace('WHEN', w)
        if send_devel:
            trigger = trigger.replace('SEND_DEVEL', 'true')
        else:
            trigger = trigger.replace('SEND_DEVEL', 'false')
        triggers += trigger
    return triggers


def get_job_name(jobtype, rosdistro, stack_name, ubuntu, arch):
    if len(stack_name) > 50:
        stack_name = stack_name[0:46]+'_...'
    return "_".join([jobtype, rosdistro, stack_name, ubuntu, arch])


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

def write_file(filename, msg):
    ensure_dir(filename)
    with open(filename, 'w') as f:
        f.write(msg)


def generate_email(message, env):
    print message
    text_xml = '<testsuite name="dummy" tests="1" errors="0" failures="0" skip="0"><testcase classname="Dummy" name="dummy" time="0"/></testsuite>'
    write_file(env['WORKSPACE']+'/build_output/buildfailures.txt', message)
    write_file(env['WORKSPACE']+'/test_output/testfailures.txt', '')
    write_file(env['WORKSPACE']+'/build_output/buildfailures-with-context.txt', '')
    write_file(env['WORKSPACE']+'/test_results/_hudson/dummy.xml', text_xml)
    write_file(env['WORKSPACE']+'/test_results/0/_hudson/dummy.xml', text_xml)


def call(command, env=None, message='', ignore_fail=False):
    res = ''
    err = ''
    try:
        print message+'\nExecuting command "%s"'%command
        helper = subprocess.Popen(command.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, env=env)
        res, err = helper.communicate()
        print str(res)
        print str(err)
        if helper.returncode != 0:
            raise Exception('bad return code')

        # command succeede, return code 0
        return res

    # command failed
    except Exception:
        if not ignore_fail:
            message += "\n=========================================\n"
            message += "Failed to execute '%s'"%command
            message += "\n=========================================\n"
            message += str(res)
            message += "\n=========================================\n"
            message += str(err)
            message += "\n=========================================\n"
            if env:
                message += "ROS_PACKAGE_PATH = %s\n"%env['ROS_PACKAGE_PATH']
                message += "ROS_ROOT = %s\n"%env['ROS_ROOT']
                message += "PYTHONPATH = %s\n"%env['PYTHONPATH']
                message += "\n=========================================\n"
                generate_email(message, env)
            raise Exception('job failed')
        return -1;


def get_sys_info():
    arch = 'i386'
    if '64' in call('uname -mrs'):
        arch = 'amd64'
    ubuntudistro = call('lsb_release -a').split('Codename:')[1].strip()
    return (arch, ubuntudistro)
