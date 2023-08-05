# -*- coding: utf-8 -*-
# vim: set et sts=2:
# pylint: disable-msg=W0311,C0301,C0103,C0111


import os
import shutil
import urllib

from flaskext.auth import Auth, AuthUser, login_required, logout
from flask import (Flask, request, redirect, url_for, render_template,
                   g, flash, jsonify, session, abort, send_file)

from slapos.runner.process import killRunningProcess
from slapos.runner.utils import (checkSoftwareFolder, configNewSR, getFolder,
                                 getFolderContent, getProfilePath,
                                 getProjectList, getProjectTitle, getSession,
                                 getSlapStatus, getSvcStatus,
                                 getSvcTailProcess, isInstanceRunning,
                                 isSoftwareRunning, isText,
                                 loadSoftwareRList, md5sum, newSoftware,
                                 readFileFrom, readParameters, realpath,
                                 removeInstanceRoot, removeProxyDb,
                                 removeSoftwareByName, runInstanceWithLock,
                                 runSoftwareWithLock, saveSession,
                                 svcStartStopProcess, svcStopAll, tail,
                                 updateInstanceParameter)

from slapos.runner.fileBrowser import FileBrowser
from slapos.runner.gittools import (cloneRepo, gitStatus, switchBranch,
                                    addBranch, getDiff, gitPush, gitPull)


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 20 * 1024 * 1024
auth = Auth(app, login_url_name='login')
auth.user_timeout = 0
file_request = FileBrowser(app.config)

# Setup default flask (werkzeug) parser
import logging
logger = logging.getLogger('werkzeug')

def login_redirect(*args, **kwargs):
  return redirect(url_for('login'))

#Access Control: Only static files and login pages are allowed to guest
@app.before_request
def before_request():
  if not request.path.startswith('/static'):
    account = getSession(app.config)
    if account:
      user = AuthUser(username=account[0])
      user.set_and_encrypt_password(account[1], "123400ZYX")
      session['title'] = getProjectTitle(app.config)
      g.users = {account[0]: user}
    else:
      session['title'] = "No account is defined"
      if request.path != "/setAccount" and request.path != "/configAccount":
        return redirect(url_for('setAccount'))

# general views
@login_required()
def home():
  return render_template('index.html')

# general views
@login_required()
def browseWorkspace():
  return render_template('workspace.html')

@app.route("/login")
def login():
  return render_template('login.html')

@app.route("/setAccount")
def setAccount():
  account = getSession(app.config)
  if not account:
    return render_template('account.html')
  return redirect(url_for('login'))

@login_required()
def myAccount():
  account = getSession(app.config)
  return render_template('account.html', username=account[0],
          email=account[2], name=account[3].decode('utf-8'))

@app.route("/dologout")
def dologout():
  _ = logout()
  return redirect(url_for('login'))

@login_required()
def configRepo():
  public_key = open(app.config['public_key'], 'r').read()
  account = getSession(app.config)
  return render_template('cloneRepository.html', workDir='workspace',
            public_key=public_key, name=account[3].decode('utf-8'),
            email=account[2])

@app.route("/doLogin", methods=['POST'])
def doLogin():
  username = request.form['clogin']
  if username in g.users:
    # Authenticate and log in!
    if g.users[username].authenticate(request.form['cpwd']):
      return jsonify(code=1, result="")
  return jsonify(code=0, result="Login or password is incorrect, please check it!")

# software views
@login_required()
def editSoftwareProfile():
  profile = getProfilePath(app.config['etc_dir'], app.config['software_profile'])
  if profile == "":
    flash('Error: can not open profile, please select your project first')
  return render_template('updateSoftwareProfile.html', workDir='workspace',
      profile=profile, projectList=getProjectList(app.config['workspace']))

@login_required()
def inspectSoftware():
  return render_template('runResult.html', softwareRoot='software_link/',
                         softwares=loadSoftwareRList(app.config))

#remove content of compiled software release
@login_required()
def removeSoftware():
  if isSoftwareRunning(app.config) or isInstanceRunning(app.config):
    flash('Software installation or instantiation in progress, cannot remove')
  elif os.path.exists(app.config['software_root']):
    svcStopAll(app.config)
    shutil.rmtree(app.config['software_root'])
    for link in os.listdir(app.config['software_link']):
      os.remove(os.path.join(app.config['software_link'], link))
    flash('Software removed')
  return redirect(url_for('inspectSoftware'))

@login_required()
def runSoftwareProfile():
  if runSoftwareWithLock(app.config):
    return  jsonify(result = True)
  else:
    return  jsonify(result = False)

@login_required()
def viewSoftwareLog():
  if os.path.exists(app.config['software_log']):
    result = tail(open(app.config['software_log'], 'r'), lines=1500)
  else:
    result = 'Not found yet'
  return render_template('viewLog.html', type='software',
      result=result.encode("utf-8"))

# instance views
@login_required()
def editInstanceProfile():
  profile = getProfilePath(app.config['etc_dir'], app.config['instance_profile'])
  if profile == "":
    flash('Error: can not open instance profile for this Software Release')
  return render_template('updateInstanceProfile.html', workDir='workspace',
      profile=profile, projectList=getProjectList(app.config['workspace']))

# get status of all computer partitions and process state
@login_required()
def inspectInstance():
  file_content = ''
  result = ''
  if os.path.exists(app.config['instance_root']):
    file_content = 'instance_root'
    result = getSvcStatus(app.config)
    if len(result) == 0:
      result = []
  return render_template('instanceInspect.html',
      file_path=file_content, supervisor=result,
      slap_status=getSlapStatus(app.config),
      supervisore=result, partition_amount=app.config['partition_amount'])

#Reload instance process ans returns new value to ajax
@login_required()
def supervisordStatus():
  result = getSvcStatus(app.config)
  if not (result):
    return jsonify(code=0, result="")
  html = "<tr><th>Partition and Process name</th><th>Status</th><th>Process PID </th><th> UpTime</th><th></th></tr>"
  for item in result:
    html += "<tr>"
    html += "<td  class='first'><b><a href='" \
        + url_for('tailProcess', process=item[0]) + "'>" \
        + item[0] + "</a></b></td>"
    html += "<td align='center'><a href='" \
        + url_for('startStopProccess', process=item[0], action=item[1]) \
        + "'>" + item[1] + "</a></td>"
    html += "<td align='center'>" + item[3] + "</td><td>" + item[5] + "</td>"
    html += "<td align='center'><a href='" \
        + url_for('startStopProccess', process=item[0], action='RESTART') \
        + "'>Restart</a></td>"
    html += "</tr>"
  return jsonify(code=1, result=html)

@login_required()
def removeInstance():
  if isInstanceRunning(app.config):
    flash('Instantiation in progress, cannot remove')
  else:
    removeProxyDb(app.config)
    svcStopAll(app.config) #Stop All instance process
    removeInstanceRoot(app.config)
    param_path = os.path.join(app.config['etc_dir'], ".parameter.xml")
    if os.path.exists(param_path):
      os.remove(param_path)
    flash('Instance removed')
  return redirect(url_for('inspectInstance'))

@login_required()
def runInstanceProfile():
  if not os.path.exists(app.config['instance_root']):
    os.mkdir(app.config['instance_root'])
  if runInstanceWithLock(app.config):
    return  jsonify(result = True)
  else:
    return  jsonify(result = False)

@login_required()
def viewInstanceLog():
  if os.path.exists(app.config['instance_log']):
    result = open(app.config['instance_log'], 'r').read()
  else:
    result = 'Not found yet'
  return render_template('viewLog.html', type='instance',
      result=result.encode("utf-8"))

@login_required()
def stopAllPartition():
  svcStopAll(app.config)
  return redirect(url_for('inspectInstance'))

@login_required(login_redirect)
def tailProcess(process):
  return render_template('processTail.html',
      process_log=getSvcTailProcess(app.config, process), process=process)

@login_required(login_redirect)
def startStopProccess(process, action):
  svcStartStopProcess(app.config, process, action)
  return redirect(url_for('inspectInstance'))

@login_required(login_redirect)
def openProject(method):
  return render_template('projectFolder.html', method=method,
                         workDir='workspace')

@login_required()
def cloneRepository():
  path = realpath(app.config, request.form['name'], False)
  data = {"repo":request.form['repo'], "user":request.form['user'],
          "email":request.form['email'], "path":path}
  return cloneRepo(data)

@login_required()
def readFolder():
  return getFolderContent(app.config, request.form['dir'])

@login_required()
def openFolder():
  return getFolder(app.config, request.form['dir'])

@login_required()
def createSoftware():
  return newSoftware(request.form['folder'], app.config, session)

@login_required()
def checkFolder():
  return checkSoftwareFolder(request.form['path'], app.config)

@login_required()
def setCurrentProject():
  if configNewSR(app.config, request.form['path']):
    session['title'] = getProjectTitle(app.config)
    return jsonify(code=1, result="")
  else:
    return jsonify(code=0, result=("Can not setup this Software Release"))

@login_required()
def manageProject():
  return render_template('manageProject.html', workDir='workspace',
                         project=getProjectList(app.config['workspace']))

@login_required()
def getProjectStatus():
  path = realpath(app.config, request.form['project'])
  if path:
    return gitStatus(path)
  else:
    return jsonify(code=0, result="Can not read folder: Permission Denied")

#view for current software release files
@login_required()
def editCurrentProject():
  project = os.path.join(app.config['etc_dir'], ".project")
  if os.path.exists(project):
    return render_template('softwareFolder.html', workDir='workspace',
                           project=open(project).read(),
                           projectList=getProjectList(app.config['workspace']))
  return redirect(url_for('configRepo'))

#create file or directory
@login_required()
def createFile():
  path = realpath(app.config, request.form['file'], False)
  if not path:
    return jsonify(code=0, result="Error when creating your " + \
                   request.form['type'] + ": Permission Denied")
  try:
    if request.form['type'] == "file":
      open(path, 'w')
    else:
      os.mkdir(path)
    return jsonify(code=1, result="")
  except Exception as e:
    return jsonify(code=0, result=str(e))

#remove file or directory
@login_required()
def removeFile():
  try:
    if request.form['type'] == "folder":
      shutil.rmtree(request.form['path'])
    else:
      os.remove(request.form['path'])
    return jsonify(code=1, result="")
  except Exception as e:
    return jsonify(code=0, result=str(e))

@login_required()
def removeSoftwareDir():
  try:
    data = removeSoftwareByName(app.config, request.form['md5'],
            request.form['title'])
    return jsonify(code=1, result=data)
  except Exception as e:
    return jsonify(code=0, result=str(e))

#read file and return content to ajax
@login_required()
def getFileContent():
  file_path = realpath(app.config, request.form['file'])
  if file_path:
    if not isText(file_path):
      return jsonify(code=0,
            result="Can not open a binary file, please select a text file!")
    if not request.form.has_key('truncate'):
      return jsonify(code=1, result=open(file_path, 'r').read())
    else:
      content = tail(open(file_path, 'r'), int(request.form['truncate']))
      return jsonify(code=1, result=content)
  else:
    return jsonify(code=0, result="Error: No such file!")

@login_required()
def saveFileContent():
  file_path = realpath(app.config, request.form['file'])
  if file_path:
    open(file_path, 'w').write(request.form['content'].encode("utf-8"))
    return jsonify(code=1, result="")
  else:
    return jsonify(code=0, result="Error: No such file!")

@login_required()
def changeBranch():
  path = realpath(app.config, request.form['project'])
  if path:
    return switchBranch(path, request.form['name'])
  else:
    return jsonify(code=0, result="Can not read folder: Permission Denied")

@login_required()
def newBranch():
  path = realpath(app.config, request.form['project'])
  if path:
    if request.form['create'] == '1':
      return addBranch(path, request.form['name'])
    else:
      return addBranch(path, request.form['name'], True)
  else:
    return jsonify(code=0, result="Can not read folder: Permission Denied")

@login_required(login_redirect)
def getProjectDiff(project):
  path = os.path.join(app.config['workspace'], project)
  return render_template('projectDiff.html', project=project,
                           diff=getDiff(path))

@login_required()
def pushProjectFiles():
  path = realpath(app.config, request.form['project'])
  if path:
    return gitPush(path, request.form['msg'])
  else:
    return jsonify(code=0, result="Can not read folder: Permission Denied")

@login_required()
def pullProjectFiles():
  path = realpath(app.config, request.form['project'])
  if path:
    return gitPull(path)
  else:
    return jsonify(code=0, result="Can not read folder: Permission Denied")

@login_required()
def checkFileType():
  path = realpath(app.config, request.form['path'])
  if not path:
    return jsonify(code=0, result="Can not open file: Permission Denied!")
  if isText(path):
    return jsonify(code=1, result="text")
  else:
    return jsonify(code=0,
                   result="Can not open a binary file, please select a text file!")

@login_required()
def getmd5sum():
  realfile = realpath(app.config, request.form['file'])
  if not realfile:
    return jsonify(code=0, result="Can not open file: Permission Denied!")
  md5 = md5sum(realfile)
  if md5:
    return jsonify(code=1, result=md5)
  else:
    return jsonify(code=0, result="Can not get md5sum for this file!")

#return information about state of slapgrid process
@login_required()
def slapgridResult():
  software_state = isSoftwareRunning(app.config)
  instance_state = isInstanceRunning(app.config)
  log_result = {"content":"", "position":0, "truncated":False}
  if request.form['log'] == "software"  or\
     request.form['log'] == "instance":
    log_file = request.form['log'] + "_log"
    if os.path.exists(app.config[log_file]):
      log_result = readFileFrom(open(app.config[log_file], 'r'),
                            int(request.form['position']))
  return  jsonify(software=software_state, instance=instance_state,
                  result=(instance_state or software_state), content=log_result)

@login_required()
def stopSlapgrid():
  result = killRunningProcess(request.form['type'])
  return jsonify(result=result)

@login_required()
def getPath():
  files = request.form['file'].split('#')
  list = []
  for p in files:
    path = realpath(app.config, p)
    if not p:
      list = []
      break
    else:
      list.append(path)
  realfile = '#'.join(list)
  if not realfile:
    return jsonify(code=0,
                   result="Can not access to this file: Permission Denied!")
  else:
    return jsonify(code=1, result=realfile)

@login_required()
def saveParameterXml():
  """
  Update instance parameter into a local xml file.
  """
  project = os.path.join(app.config['etc_dir'], ".project")
  if not os.path.exists(project):
    return jsonify(code=0, result="Please first open a Software Release")
  content = request.form['parameter'].encode("utf-8")
  param_path = os.path.join(app.config['etc_dir'], ".parameter.xml")
  try:
    f = open(param_path, 'w')
    f.write(content)
    f.close()
    result = readParameters(param_path)
  except Exception as e:
      result = str(e)
  software_type = None
  if request.form['software_type']:
    software_type = request.form['software_type']
  if type(result) == type(''):
    return jsonify(code=0, result=result)
  else:
    try:
      updateInstanceParameter(app.config, software_type)
    except Exception as e:
      return jsonify(
        code=0,
        result="An error occurred while applying your settings!<br/>" + str(e))
    return jsonify(code=1, result="")

@login_required()
def getSoftwareType():
  software_type_path = os.path.join(app.config['etc_dir'], ".software_type.xml")
  if os.path.exists(software_type_path):
    return jsonify(code=1, result=open(software_type_path, 'r').read())
  return jsonify(code=1, result="default")

#read instance parameters into the local xml file and return a dict
@login_required()
def getParameterXml(request):
  param_path = os.path.join(app.config['etc_dir'], ".parameter.xml")
  if not os.path.exists(param_path):
    default = '<?xml version="1.0" encoding="utf-8"?>\n'
    default += '<instance>\n</instance>'
    return jsonify(code=1, result=default)
  if request == "xml":
    parameters = open(param_path, 'r').read()
  else:
    parameters = readParameters(param_path)
  if type(parameters) == type('') and request != "xml":
    return jsonify(code=0, result=parameters)
  else:
    return jsonify(code=1, result=parameters)

#update user account data
@login_required()
def updateAccount():
  account = []
  account.append(request.form['username'].strip())
  account.append(request.form['password'].strip())
  account.append(request.form['email'].strip())
  account.append(request.form['name'].strip())
  code = request.form['rcode'].strip()
  recovery_code = open(os.path.join(app.config['etc_dir'], ".rcode"), "r").read()
  if code != recovery_code:
    return jsonify(code=0, result="Your password recovery code is not valid!")
  result = saveSession(app.config, account)
  if type(result) == type(""):
    return jsonify(code=0, result=result)
  else:
    return jsonify(code=1, result="")

#update user account data
@app.route("/configAccount", methods=['POST'])
def configAccount():
  last_account = getSession(app.config)
  if not last_account:
    account = []
    account.append(request.form['username'].strip())
    account.append(request.form['password'].strip())
    account.append(request.form['email'].strip())
    account.append(request.form['name'].strip())
    code = request.form['rcode'].strip()
    recovery_code = open(os.path.join(app.config['etc_dir'], ".rcode"),
                        "r").read()
    if code != recovery_code:
      return jsonify(code=0, result="Your password recovery code is not valid!")
    result = saveSession(app.config, account)
    if type(result) == type(""):
      return jsonify(code=0, result=result)
    else:
      return jsonify(code=1, result="")
  return jsonify(code=0,
                 result="Unable to respond to your request, permission denied.")

#Global File Manager
@login_required()
def fileBrowser():
  if request.method == 'POST':
    filename = request.form.get('filename', '').encode('utf-8')
    dir = request.form['dir'].encode('utf-8')
    newfilename = request.form.get('newfilename', '').encode('utf-8')
    files = request.form.get('files', '').encode('utf-8')
    if not request.form.has_key('opt') or not request.form['opt']:
      opt = 1
    else:
      opt = int(request.form['opt'])
  else:
    opt = int(request.args.get('opt'))
  try:
    if opt == 1:
      #list files and directories
      result = file_request.listDirs(dir)
    elif opt == 2:
      #Create file
      result = file_request.makeFile(dir, filename)
    elif opt == 3:
      #Create directory
      result = file_request.makeDirectory(dir, filename)
    elif opt == 4:
      #Delete a list of files or/and directories
      result = file_request.deleteItem(dir, files)
    elif opt == 5:
      #copy a lis of files or/and directories
      result = file_request.copyItem(dir, files)
    elif opt == 6:
      #rename file or directory
      result = file_request.rename(dir, filename, newfilename)
    elif opt == 7:
      result = file_request.copyItem(dir, files, del_source=True)
    elif opt == 8:
      #donwload file
      filename = request.args.get('filename').encode('utf-8')
      result = file_request.downloadFile(request.args.get('dir').encode('utf-8'),
                filename)
      try:
        return send_file(result, attachment_filename=filename, as_attachment=True)
      except:
        abort(404)
    elif opt == 9:
      result = file_request.readFile(dir, filename, False)
    elif opt == 11:
      #Upload file
      result = file_request.uploadFile(dir, request.files)
    elif opt == 14:
      #Copy file or directory as ...
      result = file_request.copyAsFile(dir, filename, newfilename)
    elif opt == 16:
      #zip file
      result = file_request.zipFile(dir, filename, newfilename)
    elif opt == 17:
      #zip file
      result = file_request.unzipFile(dir, filename, newfilename)
    else:
      result = "ARGS PARSE ERROR: Bad option..."
  except Exception as e:
    return str(e)
  return result

@login_required()
def editFile():
  return render_template('editFile.html', workDir='workspace',
    profile=urllib.unquote(request.args.get('profile', '')),
    projectList=getProjectList(app.config['workspace']),
    filename=urllib.unquote(request.args.get('filename', '')))

#Setup List of URLs
app.add_url_rule('/', 'home', home)
app.add_url_rule('/browseWorkspace', 'browseWorkspace', browseWorkspace)
app.add_url_rule('/editSoftwareProfile', 'editSoftwareProfile',
                editSoftwareProfile)
app.add_url_rule('/inspectSoftware', 'inspectSoftware', inspectSoftware)
app.add_url_rule('/removeSoftware', 'removeSoftware', removeSoftware)
app.add_url_rule('/runSoftwareProfile', 'runSoftwareProfile',
                 runSoftwareProfile, methods=['POST'])
app.add_url_rule('/viewSoftwareLog', 'viewSoftwareLog',
                 viewSoftwareLog, methods=['GET'])
app.add_url_rule('/editInstanceProfile', 'editInstanceProfile',
                 editInstanceProfile)
app.add_url_rule('/inspectInstance', 'inspectInstance',
                 inspectInstance, methods=['GET'])
app.add_url_rule('/supervisordStatus', 'supervisordStatus',
                 supervisordStatus, methods=['GET'])
app.add_url_rule('/runInstanceProfile', 'runInstanceProfile',
                 runInstanceProfile, methods=['POST'])
app.add_url_rule('/removeInstance', 'removeInstance', removeInstance)
app.add_url_rule('/viewInstanceLog', 'viewInstanceLog',
                 viewInstanceLog, methods=['GET'])
app.add_url_rule('/stopAllPartition', 'stopAllPartition',
                 stopAllPartition, methods=['GET'])
app.add_url_rule('/tailProcess/name/<process>', 'tailProcess',
                 tailProcess, methods=['GET'])
app.add_url_rule('/startStopProccess/name/<process>/cmd/<action>',
                 'startStopProccess', startStopProccess, methods=['GET'])
app.add_url_rule("/getParameterXml/<request>", 'getParameterXml',
                 getParameterXml, methods=['GET'])
app.add_url_rule('/getSoftwareType', 'getSoftwareType',
                 getSoftwareType, methods=['GET'])
app.add_url_rule("/stopSlapgrid", 'stopSlapgrid', stopSlapgrid, methods=['POST'])
app.add_url_rule("/slapgridResult", 'slapgridResult',
                 slapgridResult, methods=['POST'])
app.add_url_rule("/getmd5sum", 'getmd5sum', getmd5sum, methods=['POST'])
app.add_url_rule("/checkFileType", 'checkFileType', checkFileType,
                 methods=['POST'])
app.add_url_rule("/pullProjectFiles", 'pullProjectFiles', pullProjectFiles,
                 methods=['POST'])
app.add_url_rule("/pushProjectFiles", 'pushProjectFiles', pushProjectFiles,
                 methods=['POST'])
app.add_url_rule("/getProjectDiff/<project>", 'getProjectDiff', getProjectDiff,
                 methods=['GET'])
app.add_url_rule("/newBranch", 'newBranch', newBranch, methods=['POST'])
app.add_url_rule("/changeBranch", 'changeBranch', changeBranch, methods=['POST'])
app.add_url_rule("/saveFileContent", 'saveFileContent', saveFileContent,
                 methods=['POST'])
app.add_url_rule("/removeSoftwareDir", 'removeSoftwareDir', removeSoftwareDir,
                 methods=['POST'])
app.add_url_rule("/getFileContent", 'getFileContent', getFileContent,
                 methods=['POST'])
app.add_url_rule("/removeFile", 'removeFile', removeFile, methods=['POST'])
app.add_url_rule("/createFile", 'createFile', createFile, methods=['POST'])
app.add_url_rule("/editCurrentProject", 'editCurrentProject', editCurrentProject)
app.add_url_rule("/getProjectStatus", 'getProjectStatus', getProjectStatus,
                 methods=['POST'])
app.add_url_rule('/openProject/<method>', 'openProject', openProject,
                 methods=['GET'])
app.add_url_rule("/manageProject", 'manageProject', manageProject, methods=['GET'])
app.add_url_rule("/setCurrentProject", 'setCurrentProject', setCurrentProject,
                 methods=['POST'])
app.add_url_rule("/checkFolder", 'checkFolder', checkFolder, methods=['POST'])
app.add_url_rule('/createSoftware', 'createSoftware', createSoftware,
                 methods=['POST'])
app.add_url_rule('/cloneRepository', 'cloneRepository', cloneRepository,
                 methods=['POST'])
app.add_url_rule('/openFolder', 'openFolder', openFolder, methods=['POST'])
app.add_url_rule('/readFolder', 'readFolder', readFolder, methods=['POST'])
app.add_url_rule('/configRepo', 'configRepo', configRepo)
app.add_url_rule("/saveParameterXml", 'saveParameterXml', saveParameterXml,
                 methods=['POST'])
app.add_url_rule("/getPath", 'getPath', getPath, methods=['POST'])
app.add_url_rule("/myAccount", 'myAccount', myAccount)
app.add_url_rule("/updateAccount", 'updateAccount', updateAccount,
                 methods=['POST'])
app.add_url_rule("/fileBrowser", 'fileBrowser', fileBrowser,
                 methods=['GET', 'POST'])
app.add_url_rule("/editFile", 'editFile', editFile, methods=['GET'])
