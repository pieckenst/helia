import discord
import asyncio
import functools
import os
import sqlite3
from scripts import db, help
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
class welcome(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        try:
            connect = sqlite3.connect(db.main)
            cursor = connect.cursor()
            cursor.execute(db.select_table("welcome", "channel_id", "guild_id", member.guild.id)) 
            chan = cursor.fetchone()
            if chan is None:
                return
            else:
                cursor.execute(db.select_table("welcome", "text", "guild_id", member.guild.id))
                desc = cursor.fetchone()
                if desc is None: 
                    desc = f" Hi there {MEMBER} and welcome to our humble community"
                hello = discord.Embed(title="Hello there", description=(desc[0]).format(MEMBER=member, MENTION=member.mention), color=0x00ff00)
                hello.set_author(name=f"{member.guild}", icon_url=f"{member.guild.icon_url}")
                hello.set_thumbnail(url=f"{member.avatar_url}")
                channel = self.bot.get_channel(id=int(chan[0]))
                await channel.send(embed=hello)      
            cursor.close()
            connect.close()
        except:
            print(f"The server  {member.guild.id} encountered an unknown error. Perhaps the welcome channel was removed.")

       


        
    @commands.group(invoke_without_command=True)
    async def welcome(self, ctx: SlashContext):
        await ctx.send(help.welcome)

    @welcome.command(pass_context=True)
    async def channel(self, ctx: SlashContext, chan: discord.TextChannel=None):
        try:
            author = ctx.message.author     
            if author.guild_permissions.administrator:
                connect = sqlite3.connect(db.main)
                cursor = connect.cursor()   
                cursor.execute(db.select_table("welcome", "channel_id", "guild_id", ctx.guild.id)) 
                res = cursor.fetchone()
                if res is None:
                    val = (ctx.guild.id, chan.id)
                    cursor.execute(db.insert_table("welcome","guild_id","channel_id"), val)
                else:
                    cursor.execute(db.update_table("welcome", "channel_id", chan.id, "guild_id", ctx.guild.id))  
                connect.commit()
                cursor.close()
                connect.close()
                await ctx.send(f"bot: Set the welcome channel to {chan.mention}")  
            else:
                await ctx.send("You do not have enough permissions - :You require **Administrator**.")  
        except:
            await ctx.send("bot: Error")    


    @welcome.command(pass_context=True)
    async def clear(self, ctx: SlashContext):
        try:
            author = ctx.message.author
            if author.guild_permissions.administrator:
                connect = sqlite3.connect(db.main)
                cursor = connect.cursor()
                cursor.execute(db.select_table("welcome", "channel_id", "guild_id", ctx.guild.id))
                res = cursor.fetchone()
                if res is None:
                    await ctx.send("bot: Do not have a table for the welcome channel - Check Database.")
                else:
                    cursor.execute(db.delete_table("welcome", "guild_id", ctx.guild.id))
                    await ctx.send("bot: Cleared the table")
                connect.commit()
                cursor.close()
                connect.close()
            else:
                await ctx.send("You do not have enough permissions - :You require **Administrator**.")
        except:
            await ctx.send("bot: Error")
    
    @welcome.command(pass_context=True)
    async def text(self, ctx: SlashContext,*,content=None):
        try:    
            author = ctx.message.author
            if author.guild_permissions.administrator:
                if content is None:
                    return await ctx.send("bot: Please type the text you wish for the welcome message")
                connect = sqlite3.connect(db.main)
                cursor = connect.cursor()
                cursor.execute(db.select_table("welcome", "text", "guild_id", ctx.guild.id))
                res = cursor.fetchone()
                if res is None:
                    val = (ctx.guild.id, content)
                    cursor.execute(db.insert_table("welcome","guild_id","text"), val)
                else:
                    val = (content, ctx.guild.id)
                    cursor.execute("UPDATE welcome SET text = ? WHERE guild_id = ?", val)      
                connect.commit()
                cursor.close()
                connect.close()
                await ctx.send(f"bot: Set the welcome message text") 
            else:
                await ctx.send("bot: You do not have enough permissions - :You require **Administrator**.")
        except:
            await ctx.send("bot: Error , argument may be invalid")




       
def setup(bot):
    bot.add_cog(welcome(bot))
