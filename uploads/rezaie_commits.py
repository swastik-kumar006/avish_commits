# Made by @e3ris for Ultroid.

import os
import asyncio
import requests
from shutil import rmtree as rt
try:
	from github import Github
except Exception:
	os.system("pip install PyGithub")
	from github import Github

from . import *

folda = "resources/commits/"
commit_default_msg = "Committed from UserBot by Rezaie!"
errors_ = int(Redis("LOG_CHANNEL"))
branch_ = "main"
# repo: https://github.com/aviskumar/avish_commits/tree/main/uploads

@ultroid_cmd(pattern="commit ?(.*)")
async def git_commit(e):
	if e.fwd_from:
		return
	y = udB.get("GIT_TOKEN")
	x = udB.get("GIT_REPO")
	all_files = list()
	if y == None or x == None:
		return await eod(e, "`GIT data unavailable`")
	from random import randrange as rr
	rr = rr(2, 2**16)
	eris = await eor(e, "__downloading__")
	reply = await e.get_reply_message()
	if not (reply and reply.media):
		return await eod(eris, "`Reply to a file ...`")
	args = e.pattern_match.group(1)
	if not args: args = commit_default_msg
	ext = reply.file.ext
	hmn = humanbytes(reply.file.size)
	fn = (
		reply.file.name 
		if reply.file.name
		else f"Ultroid commits_{rr} (Powered by PyGithub){ext}"
	)
	file_name = fn.replace(" ", "_")
	try:
		if hmn.split()[0] > str(50):
			return await eris.edit("`File size crosses the limits of GitHub! exiting...`")
		download = await reply.download_media(f"{folda}{file_name}")
	except Exception:
		return await eris.edit(f"`Error while Downloading the file.`")

	try:
		with open(download, "rb") as file:
			content = file.read()
	except Exception as exx:
		return await eris.edit("**Invalid File.**")
	finally:
		rt(folda)
	await eris.edit("__file downloaded successfully!__")
	await asyncio.sleep(1)
	git3 = Github(y)
	repo = git3.get_user().get_repo(x)
	contents = repo.get_contents("")
	while contents:
		file_content = contents.pop(0)
		if file_content.type == "dir":
			contents.extend(repo.get_contents(file_content.path))
		else:      	 
			file = file_content
			all_files.append(str(file).replace('ContentFile(path="','').replace('")',''))
	# Upload to github
	git_file = f"uploads/{file_name}"
	git_info = f"rez4ie/{x}"
	if git_file in all_files:
		contents = repo.get_contents(git_file)
		repo.update_file(contents.path, f"{args}", content, contents.sha, branch=branch_)
	else:
		repo.create_file(git_file, f"{args}", content, branch=branch_)

	git_raw_link = f"https://raw.githubusercontent.com/{git_info}/main/{git_file}"
	git_folder_link = f"https://github.com/{git_info}/tree/main/uploads"
	git_direct_link = f"https://github.com/{git_info}/blob/main/{git_file}"
	await eris.delete()
	links = f"<b>»»</b> Uploaded to • <a href='{git_folder_link}'>GitHub</a> •</b> \n\n"
	links += f'<b>-> 📃 <a href="{git_raw_link}"> Raw Link</a>\n'
	links += f'-> ⚡ <a href="{git_direct_link}"> Direct Link</a> </b>'
	await reply.reply(links, parse_mode="html", link_preview=False)
