#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, commands
import ConfigParser
from time import strftime

global logfile
logfile = open('/var/log/tuquitoajustes.log', 'w')

def log (string):
	logfile.writelines("%s - %s\n" % (strftime("%Y-%m-%d %H:%M:%S"), string))
	logfile.flush()

log('tuquito-ajustes iniciado')

try:
	# Lee la configuración
	config = ConfigParser.ConfigParser()
	config.read('/etc/tuquito/tuquito-ajustes.conf')
	enabled = config.getboolean("Global", "enabled")
	lsbRelease = config.getboolean("Restore", "lsb-release")
	etcIssue = config.getboolean("Restore", "etc-issue")

	# Sale si está desabilitado
	if not enabled:
		log('Desabilitado - Detenido')
		exit(0)

	# Ajustes de sobreescritura de archivos
	adjustmentDirectory = '/etc/tuquito/ajustes/'
	arrayPreserves = []
	if os.path.exists(adjustmentDirectory):
		for filename in os.listdir(adjustmentDirectory):
			basename, extension = os.path.splitext(filename)
			if extension == '.preserve':
				filehandle = open(adjustmentDirectory + '/' + filename)
				for line in filehandle:
					line = line.strip()
					arrayPreserves.append(line)
				filehandle.close()
	overwrites = {}
	if os.path.exists(adjustmentDirectory):
		for filename in sorted(os.listdir(adjustmentDirectory)):
			basename, extension = os.path.splitext(filename)
			if extension == '.overwrite':
				filehandle = open(adjustmentDirectory + '/' + filename)
				for line in filehandle:
					line = line.strip()
					lineItems = line.split()
					if len(lineItems) == 2:
						source, destination = line.split()
						if destination not in arrayPreserves:
							overwrites[destination] = source
				filehandle.close()

	for key in overwrites.keys():
		source = overwrites[key]
		destination = key
		if os.path.exists(source):
			if not '*' in destination:
				if os.path.exists(destination):
					os.system('cp ' + source + ' ' + destination)
					log(destination + ' reemplazado por ' + source)
			else:
				matchingDestinations = commands.getoutput('find ' + destination)
				matchingDestinations = matchingDestinations.split('\n')
				for matchingDestination in matchingDestinations:
					matchingDestination = matchingDestination.strip()
					if os.path.exists(matchingDestination):
						os.system('cp ' + source + ' ' + matchingDestination)
						log(matchingDestination + ' reemplazado por ' + source)

	# Restaura la información LSB
	if lsbRelease:
		if os.path.exists('/etc/lsb-release'):
			lsbfile = open('/etc/lsb-release', 'w')
			lsbfile.writelines('DISTRIB_ID=Tuquito\n')
			lsbfile.writelines('DISTRIB_' + commands.getoutput('grep RELEASE /etc/tuquito/info') + '\n')
			lsbfile.writelines('DISTRIB_' + commands.getoutput('grep CODENAME /etc/tuquito/info') + '\n')
			lsbfile.writelines('DISTRIB_' + commands.getoutput('grep DESCRIPTION /etc/tuquito/info') + '\n')
			lsbfile.close()
			log('/etc/lsb-release restaurado')

	# Restaura /etc/issue y /etc/issue.net
	if etcIssue:
		issue = commands.getoutput('grep DESCRIPTION /etc/tuquito/info').replace('DESCRIPTION=', '').replace('"', '')
		if os.path.exists('/etc/issue'):
			issuefile = open('/etc/issue', 'w')
			issuefile.writelines(issue + ' \\n \\l\n')
			issuefile.close()
			log('/etc/issue restaurado')
		if os.path.exists('/etc/issue.net'):
			issuefile = open('/etc/issue.net', 'w')
			issuefile.writelines(issue + '\n')
			issuefile.close()
			log('/etc/issue.net restaurado')

except Exception, detail:
	print detail
	log(detail)

log('tuquito-ajustes finalizado')
logfile.close()
