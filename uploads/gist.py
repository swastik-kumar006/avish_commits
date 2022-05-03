# Made by @e3ris for Ultroid!

import aiohttp
import asyncio
import json
import re

from os import remove
from uuid import uuid4
from telethon.errors.rpcerrorlist import (
    ChatSendInlineForbiddenError,
    BotMethodInvalidError,
)

from . import *


API_ = "https://api.github.com/gists"
LINK_ = "https://gist.github.com/{0}"
BTNS = """[
    [Button.url("Raw", url="{0}"),
    Button.inline("❌", data="delgist_{1}"),
    Button.url("Gist", url="{2}")],
]"""


@ultroid_cmd(pattern="gist(?: |$)((?:.|\n)*)")
async def gistify(e):
    if not udB.get_key("GIST_TOKEN"):
        return await e.eor("`GIST_TOKEN` not found, quitting!", time=30)
    eris = await e.eor("`pasting...`")
    reply = await e.get_reply_message()
    args = e.pattern_match.group(1)
    filename = None
    if args:
        data = args
    elif reply:
        if reply.document:
            filename = reply.file.name
            if reply.file.size > 15*1024*1024:
                return await eris.edit(
                    "File Size is Gretaer than 10MB! quitting")
            dls = await reply.download_media()
            try:
                with open (dls, "r") as f:
                    data = f.read()
                remove(dls)
            except:
                return await eris.edit(f"Couldn't read this file.")
        elif reply.text:
            data = reply.message
        else:
            return await eris.edit("Unsupported Media!")
    else:
        return await eris.edit("Give Some text to paste!")

    gist_id = await gistify(filename=filename, data=data)
    if not gist_id:
        return await eris.edit("**Something went Wrong!**")
    try:
        inlone = await e.client.inline_query(asst.me.username,
            "GIST " + gist_id, entity=e.chat_id)
        await inlone[0].click(reply_to=e.reply_to_msg_id, silent=True)
        await eris.delete()
    except BotMethodInvalidError:
        return await eris.edit("**Pasted to Gist !!**", buttons=eval(BTNS.format(
            LINK_.format(f"raw/{gist_id}"), gist_id, LINK_.format(gist_id))))
    except ChatSendInlineForbiddenError:
        links = f"**Pasted to Gist!** \n»»  [Direct]({LINK_.format(gist_id)})" \
            f" \n»»  [Raw]({LINK_.format('raw/' + gist_id)})"
        await eris.edit(links, parse_mode="html", link_preview=False)
    except Exception as ex:
        return await eris.edit(f"**Something Wrong!** \n> `{ex}`")


@in_pattern("GIST", owner=True)
async def inlinegist(e):
    try:
        resp = e.text.split(maxsplit=1)[1]
    except:
        return await e.answer([])
    await e.answer([e.builder.article(
        text="**Pasted to Gist !!**ㅤ",
        title="Gistified • Ultroid",
        description="Made by @e3ris\n@testingpluginnn",
        buttons=eval(BTNS.format(
            LINK_.format(f"raw/{resp}"), resp, LINK_.format(resp))))])


@callback(re.compile("delgist_(.*)"), owner=True)
async def deletemee(e):
    gid = e.data_match.group(1).decode("utf-8")
    await e.answer("🌩️ Trying to delete your Gist !! 🌩️")
    to_del = await gistify(delete=True, gist_id=gid)
    await asyncio.sleep(1.5)
    if to_del:
        return await e.edit("__Gist Deleted!__")
    return await e.answer("Error while deleteing Gist ; " \
        "Go check LOGS", alert=True)


async def gistify(**args):
    desc = f"Posted by {ultroid.full_name} from Telegram!"
    headers = {"Authorization": "token " + udB.get_key("GIST_TOKEN"), "User-Agent": "Ghost_python_bot/1.1.7"}
    async with aiohttp.ClientSession(headers=headers) as cli:
        if args.get("delete"):
            req = await cli.request("DELETE", f"{API_}/{args['gist_id']}")
            if req.status in [200, 201, 204]:
                return True
            LOGS.error(str(await req.text()))
            return
        else:
            fn = args.get("filename") or str(uuid4().hex)[:6] + ".txt"
            req = await cli.request("POST", API_,
                json={
                    "description": args.get("description") or desc,
                    "public": args.get("public") or False,
                    "files": {fn: {"content": args.get("data")}},
                })
            if req.status in [201, 204, 200]:
                r = await req.json()
                return r.get("id")
            else:
                LOGS.error(str(await req.text()))
                return
