
from discord.ext import commands
import discord


class Admin(commands.Cog):
    def __init__(self, bot, dev_guild_id=756190406642761869):
        '''
        Initializes the Admin cog.
        '''
        self.dev_guild_id = dev_guild_id
        self.bot = bot

    @commands.command(name="sync", description="Sync bot commands")
    @commands.is_owner()
    async def sync(self, ctx):
        '''
        Syncs the bot commands with Discord.
        '''

        try:
            print("Syncing commands...")
            commands_to_sync = self.bot.tree.get_commands()
            command_names = [command.name for command in commands_to_sync]
            await ctx.send(f"Commands to sync: {', '.join(command_names)}")
            
            synced = await self.bot.tree.sync()
            await ctx.send(f"Synced {len(synced)} commands.")
        except Exception as e:
            await ctx.send(f"Error syncing commands: {e}")

    @commands.command(name="clear", description="Clear all slash commands")
    @commands.is_owner()
    async def clear(self, ctx):
        '''
        Clears all slash commands from the bot.
        '''

        try:
            print("Clearing commands...")
            commands_to_clear = self.bot.tree.get_commands()
            command_names = [command.name for command in commands_to_clear]
            await ctx.send(f"Commands to clear: {', '.join(command_names)}")

            guild = discord.Object(id=self.dev_guild_id)
            self.bot.tree.clear_commands(guild=guild)
            await self.bot.tree.sync(guild=guild)
            await ctx.send("All commands cleared for the development guild.")
        except Exception as e:
            await ctx.send(f"Error clearing commands: {e}")


async def setup(bot):
    await bot.add_cog(Admin(bot))