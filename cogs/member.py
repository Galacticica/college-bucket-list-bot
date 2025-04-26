import discord
from discord.ext import commands
from discord import app_commands
import psycopg2
from dotenv import load_dotenv
import os
import asyncio
import aiohttp  # Add this import for downloading the image
import os       # Add this import for file handling

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class Member(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="complete", description="Complete a bucket list item (requires an image or video)")
    async def complete(self, interaction: discord.Interaction, item_number: int):
        try:
            await interaction.response.send_message(
                "Please reply with an image or video to complete this item.", ephemeral=True
            )

            def check(message: discord.Message):
                return (
                    message.author == interaction.user
                    and message.channel == interaction.channel
                    and message.attachments
                )

            try:
                message = await self.bot.wait_for("message", timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await interaction.followup.send(
                    "You did not reply with an image or video in time. Please try again.", ephemeral=True
                )
                return

            attachment_url = message.attachments[0].url

            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE "user-items"
                SET status = TRUE
                WHERE userid = %s AND itemid = %s;
            ''', (interaction.user.id, item_number))

            cursor.execute('''
                SELECT item
                FROM "bucketlist"
                WHERE id = %s;
            ''', (item_number,))
            item = cursor.fetchone()
            item_name = item[0]

            cursor.execute('''
                UPDATE "user-items"
                SET image_url = %s
                WHERE userid = %s AND itemid = %s;
            ''', (attachment_url, interaction.user.id, item_number))

            conn.commit()
            cursor.close()
            conn.close()

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(attachment_url) as response:
                        if response.status == 200:
                            with open("temp_image.jpg", "wb") as f:
                                f.write(await response.read())

                with open("temp_image.jpg", "rb") as image_file:
                    discord_file = discord.File(image_file, filename="completed_item.jpg")
                    embed = discord.Embed(
                        title=f"{item_name} Completed!",
                        description=f"{interaction.user.mention} marked '{item_name}' as complete.",
                        color=discord.Color.green()
                    )
                    embed.set_image(url="attachment://completed_item.jpg")

                    await interaction.channel.send(embed=embed, file=discord_file)

                os.remove("temp_image.jpg")
            except Exception as e:
                await interaction.followup.send(f"Error: {e}", ephemeral=True)

            await message.delete()
        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)

    @app_commands.command(name="incomplete", description="Mark a bucket list item as incomplete")
    async def incomplete(self, interaction: discord.Interaction, item_number: int):
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE "user-items"
                SET status = FALSE
                WHERE userid = %s AND itemid = %s;
            ''', (interaction.user.id, item_number))

            cursor.execute('''
                UPDATE "user-items"
                SET image_url = NULL
                WHERE userid = %s AND itemid = %s;
            ''', (interaction.user.id, item_number))

            cursor.execute('''
                SELECT item
                FROM "bucketlist"
                WHERE id = %s;
            ''', (item_number,))
            item = cursor.fetchone()
            item_name = item[0]

            conn.commit()
            cursor.close()
            conn.close()

            await interaction.response.send_message(f"{item_name} marked as incomplete, and the image has been removed.")
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")

    @app_commands.command(name="list", description="List all bucket list items")
    async def list_items(self, interaction: discord.Interaction):
        try:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            cursor = conn.cursor()

            cursor.execute('''
                SELECT b.id, b.item, ui.status
                FROM "bucketlist" b
                JOIN "user-items" ui ON b.id = ui.itemid
                WHERE ui.userid = %s
                ORDER BY b.id;
            ''', (interaction.user.id,))
            items = cursor.fetchall()

            embed = discord.Embed(
                title="Your Bucket List",
                description="Here are your bucket list items:",
                color=discord.Color.blue()
            )

            if items:
                for index, item in enumerate(items, start=1):
                    status = "✅ Complete" if item[2] else "❌ Incomplete"
                    embed.add_field(
                        name=f"{index}. {item[1]}",
                        value=f"Status: {status}",
                        inline=False
                    )
            else:
                embed.description = "No items found."

            conn.commit()
            cursor.close()
            conn.close()

            await interaction.response.send_message(embed=embed)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}")

async def setup(bot):
    await bot.add_cog(Member(bot))
