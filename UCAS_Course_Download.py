# -*- coding:utf8 -*-


import requests
import re
from bs4 import BeautifulSoup
import os
import time


def file_download(url, fileName, className, session, folder):
	dir_base = os.getcwd() + "/" + className
	dir = dir_base + "/"  + folder
	file = dir + fileName
	# create folder
	if not os.path.exists(dir_base):
		os.mkdir(dir_base)
	if not os.path.exists(dir):
		os.mkdir(dir)
	# have such file
	if os.path.exists(file):
		print("File already exists: " + fileName )
		return
	print("Start download: " + fileName )
	s = session.get(url)
	with open(file, "wb") as data:
		data.write(s.content)


def errorExit(msg):
	print(msg)
	os.system("pause")
	exit()


def getClass(currentClass, url, session, data, base_url):

	#file
	s = session.get(url)
	file_indexs = BeautifulSoup(s.text, "html.parser").find_all("li", {"class":"file"})
	for file_index in file_indexs:
		file_index_base = file_index.a.get("href")
		download_url = url + file_index_base
		folder = url.replace(base_url , "")
		file_download(download_url, file_index_base, currentClass, session , folder)

	#folder
	s = session.get(url)
	folder_indexs = BeautifulSoup(s.text, "html.parser").find_all("li", {"class":"folder"})
	for folder_index in folder_indexs:
		folder_index_base = folder_index.a.get("href")
		next_url = url + folder_index_base
		getClass(currentClass, next_url, session, data, base_url)

if __name__ == '__main__':
	username = input("Please input your username: ")
	password = input("Please input your password: ")
	print("Your Login ID：" + username)
	try:
		session = requests.Session()
		s = session.get(
			"http://sep.ucas.ac.cn/slogin?userName=" + username + "&pwd=" + password + "&sb=sb&rememberMe=1");
		bsObj = BeautifulSoup(s.text, "html.parser")
		nameTag = bsObj.find("li", {"class": "btnav-info", "title": "当前用户所在单位"})
		if nameTag == None:
			errorExit("Login Failed")
		name = nameTag.get_text()
		match = re.compile(r"\s*(\S*)\s*(\S*)\s*").match(name)
		if (match):
			name = match.group(2)
			print("Welcome," + name)
		else:
			errorExit("Login failed")

		s = session.get("http://sep.ucas.ac.cn/portal/site/16/801")
		bsObj = BeautifulSoup(s.text, "html.parser")

		newUrl = bsObj.find("noscript").meta.get("content")[6:]
		s = session.get(newUrl)
		bsObj = BeautifulSoup(s.text, "html.parser").find("a", {"class": "Mrphs-toolsNav__menuitem--link ","title":"我的课程 - 查看或加入站点"})
		newUrl = bsObj.get("href")
		s = session.get(newUrl)
		classList = []
		trList = BeautifulSoup(s.text, "html.parser").findAll("tr")
		del trList[0]
		for tr in trList:
			tdList = tr.findAll("th")
			className = tr.find("a").get_text().strip()
			classWebsite = tr.find("a").get("href")
			class_source_num = re.findall(r"site/(.+)", classWebsite)[0]
			classList.append((className, classWebsite,class_source_num));
		print("You have such " + str(len(classList)) + " classes: ")

		for c in classList:
			dir_base = os.getcwd() + "/" + c[0]
			if not os.path.exists(dir_base):
				os.mkdir(dir_base)
			print("(" + c[0] + ")")
		print("\n")
		print("Start download......")
		for c in classList:
			url = "http://course.ucas.ac.cn/access/content/group/" + c[2] + "/"
			s = session.get(url)
			getClass(c[0], url, session, None, url)
	except NameError:
		errorExit("Down failed")
	print("\n")