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
	glob = config.get("Global", "enabled")
	lsbRelease = config.get("Restore", "lsb-release")
	etcIssue = config.get("Restore", "etc-issue")
	etcMotd = config.get("Restore", "etc-motd")

	# Sale si está desabilitado
	if glob == 'False':
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
	if lsbRelease == 'True':
		if os.path.exists('/etc/lsb-release'):
			lsbfile = open('/etc/lsb-release', 'w')
			lsbfile.writelines('DISTRIB_ID=Tuquito\n')
			lsbfile.writelines('DISTRIB_' + commands.getoutput('cat /etc/tuquito/info | grep RELEASE') + '\n')
			lsbfile.writelines('DISTRIB_' + commands.getoutput('cat /etc/tuquito/info | grep CODENAME') + '\n')
			lsbfile.writelines('DISTRIB_' + commands.getoutput('cat /etc/tuquito/info | grep DESCRIPTION') + '\n')
			lsbfile.close()
			log('/etc/lsb-release restaurado')

	# Restaura /etc/issue y /etc/issue.net
	if etcIssue == 'True':
		issue = commands.getoutput('cat /etc/tuquito/info | grep DESCRIPTION').replace('DESCRIPTION=', '').replace('"', '')
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

	# Restaura /etc/motd y /etc/motd.tail
	if etcMotd == 'True':
		text = 'Documentación oficial de Tuquito:\nhttp://tukipedia.tuquito.org.ar\n'
		if os.path.exists('/etc/motd.tail'):
			issuefile = open('/etc/motd.tail', 'w')
			issuefile.writelines(text)
			issuefile.close()
			log('/etc/motd.tail restaurado')
		if os.path.exists('/var/run/motd'):
			issuefile = open('/var/run/motd', 'w')
			issuefile.writelines(text)
			issuefile.close()
			log('/var/run/motd restaurado')

except Exception, detail:
	print detail
	log(detail)

log('tuquito-ajustes finalizado')
logfile.close()
